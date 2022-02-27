import functools
import logging
import os
from typing import List, Tuple
from unittest import mock

import google.auth.transport.requests
import google.oauth2.id_token
import jwt
from firebase_admin import auth
from google.auth.transport.requests import Request
from google.oauth2 import id_token
from rest_framework.exceptions import (
    AuthenticationFailed,
    PermissionDenied,
    ValidationError,
)

from .firebase import FirebaseHelper

logger = logging.getLogger(__name__)


def auth_request_firebase(request) -> Tuple[dict, auth.UserRecord]:
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
            return payload, user
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
                _, req.firebase_user = auth_request_firebase(req)
            if oidc:
                req.oidc_data = auth_request_oidc(req)

            # run req_handler
            return req_handler(*args, **kwargs)

        return wrapper

    return decorator


def authorize(request, data: dict, org_roles: List[str], group_roles: List[str] = []):
    if "organisation_id" not in request.data:
        raise ValidationError({"organisation_id": ["This field is required."]})

    org_id = request.data["organisation_id"]
    org = data.get("organisations", {}).get(org_id, {})

    if org.get("org_role") not in org_roles:
        raise PermissionDenied()

    if "GROUP_USER" in org_roles:
        if "group_id" not in request.data:
            raise ValidationError({"group_id": ["This field is required."]})

        group_id = request.data["group_id"]

        if org.get("g", {}).get(group_id, {}).get("group_role") not in group_roles:
            raise PermissionDenied()


def auth_org_user(
    *, firebase: bool, oidc: bool, org_roles: List[str], group_roles: List[str] = []
):
    """
    Auth decorator that supports firebase and OIDC token

    Args:
        firebase (bool): if True, authenticate firebase token
        oidc (bool): if True, authenticate OIDC token
        org_role (str)
        group_role (str)
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
                data, req.firebase_user = auth_request_firebase(req)
                authorize(req, data, org_roles, group_roles=group_roles)
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
