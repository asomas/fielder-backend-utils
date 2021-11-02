import functools
import logging
import os
from typing import List
from unittest import mock

import google.auth.transport.requests
import google.oauth2.id_token
import jwt
from firebase_admin.auth import UserRecord
from google.auth.transport.requests import Request
from google.oauth2 import id_token
from rest_framework.exceptions import (
    AuthenticationFailed,
    NotFound,
    PermissionDenied,
    ValidationError,
)

from .firebase import FirebaseHelper

logger = logging.getLogger(__name__)


def auth_request_firebase(request) -> UserRecord:
    """
    Authenticate firebase id_token and get firebase user
    Args:
        request (Request): DRF request
    """
    firestore = FirebaseHelper.getInstance()
    try:
        if "X-Forwarded-Authorization" in request.headers:
            token = request.headers["X-Forwarded-Authorization"].split(" ").pop()
        else:
            token = request.headers["Authorization"].split(" ").pop()
        if os.getenv("ASOMAS_SERVER_MODE", "").lower() in ["local", "test"]:
            payload = jwt.decode(token, options={"verify_signature": False})
            user = mock.Mock()
            user.uid = payload["user_id"]
            if "phone_number" in payload:
                user.phone_number = payload["phone_number"]
            if "email" in payload:
                user.email = payload["email"]
            if "display_name" in payload:
                user.display_name = payload["display_name"]
            return user
        else:
            return firestore.authenticate(token)
    except Exception as e:
        logger.warning(e)
        raise AuthenticationFailed(detail="invalid firebase authentication header")


def auth_request_oidc(request) -> dict:
    """
    Authenticate oidc id_token and get jwt info as dict
    Args:
        request (Request): DRF request
    Returns:
        data (dict): data from token
    """
    try:
        if os.getenv("ASOMAS_SERVER_MODE", "").lower() in ["local", "test"]:
            # pubsub emulator doesn't send authorization header
            # https://github.com/googleapis/google-cloud-java/issues/1381#issuecomment-259427949
            if "Authorization" in request.headers:
                token = request.headers["Authorization"].split(" ").pop()
            else:
                # {"email": "fielder-emulator@appspot.gserviceaccount.com"}
                token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJlbWFpbCI6ImZpZWxkZXItZW11bGF0b3JAYXBwc3BvdC5nc2VydmljZWFjY291bnQuY29tIn0.PRDpQejYLbKTSrkXsq_LxjF_u_LeeQJpKB_1o1h7jqo"
            return jwt.decode(token, options={"verify_signature": False})
        else:
            token = request.headers["Authorization"].split(" ").pop()
            req = google.auth.transport.requests.Request()
            return google.oauth2.id_token.verify_oauth2_token(token, req)
    except Exception as e:
        logger.warning(e)
        raise AuthenticationFailed(detail="invalid oidc authorization header")


def auth(firebase: bool = True, oidc: bool = True):
    """
    Auth decorator that supports firebase and OIDC token

    Args:
        firebase (bool): if True, authenticate firebase token
        oidc (bool): if True, authenticate OIDC token
    """

    def decorator(req_handler):
        @functools.wraps(req_handler)
        def wrapper(*args, **kwargs):
            # assume request object is one
            # of the args
            req = None
            for arg in args:
                if type(arg).__name__.lower() == "request":
                    req = arg
                    req.firebase_user = None
                    req.oidc_data = None
                    break
            if not req:
                raise RuntimeError("no rest_framework.request.Request in args")

            # authenticate
            if firebase:
                req.firebase_user = auth_request_firebase(req)
            if oidc:
                req.oidc_data = auth_request_oidc(req)

            # run req_handler
            return req_handler(*args, **kwargs)

        return wrapper

    return decorator


def authorize(request, restricted_roles):
    fs = FirebaseHelper.getInstance()

    if "organisation_id" not in request.data:
        raise ValidationError({"organisation_id": ["This field is required."]})

    organisation_ref = fs.db.collection("organisations").document(
        request.data["organisation_id"]
    )
    organisation_snapshot = organisation_ref.get()
    if not organisation_snapshot.exists:
        raise NotFound(detail="Organisation not found.")

    organisation_user_ref = fs.db.collection("organisation_users").document(
        request.firebase_user.uid
    )

    organisation_user_snapshot = organisation_user_ref.get()
    if not organisation_user_snapshot.exists:
        raise NotFound(detail="Organisation User not found.")

    organisation_user_data = organisation_user_snapshot.to_dict()
    organisations = organisation_user_data.get("organisations")
    if (not isinstance(organisations, dict)) or (
        not organisations.get(organisation_ref.id, None)
    ):
        raise PermissionDenied(detail="You are not part of this organisation.")

    role = organisations[organisation_ref.id].get("role", None)
    if (not role) or (role not in restricted_roles):
        raise PermissionDenied(
            detail="You don't have enough permission for that action."
        )


def auth_organisation_user(*, restricted_roles: List, firebase: bool, oidc: bool):
    """
    Auth decorator that supports firebase and OIDC token

    Args:
        restricted_roles (List): ["owner", "admin", "hr", "manager", "supervisor"]
        firebase (bool): if True, authenticate firebase token
        oidc (bool): if True, authenticate OIDC token
    """

    def decorator(req_handler):
        @functools.wraps(req_handler)
        def wrapper(*args, **kwargs):
            # assume request object is one
            # of the args
            req = None
            for arg in args:
                if type(arg).__name__.lower() == "request":
                    req = arg
                    req.firebase_user = None
                    req.oidc_data = None
                    break
            if not req:
                raise RuntimeError("no rest_framework.request.Request in args")

            # authenticate
            if firebase:
                req.firebase_user = auth_request_firebase(req)
                authorize(req, restricted_roles)
            if oidc:
                req.oidc_data = auth_request_oidc(req)

            # run req_handler
            return req_handler(*args, **kwargs)

        return wrapper

    return decorator


def get_oidc_token(
    audience: str = "https://www.googleapis.com/auth/cloud-platform.read-only",
):
    return id_token.fetch_id_token(Request(), audience)
