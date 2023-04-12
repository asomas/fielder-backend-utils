import functools
import logging
import os
from typing import List, Tuple
from unittest import mock

import google.auth.transport.requests
import google.oauth2.id_token
import jwt
from firebase_admin.auth import UserRecord
from google.auth.transport.requests import Request
from google.oauth2 import id_token
from rest_framework.exceptions import (
    AuthenticationFailed,
    NotAuthenticated,
    PermissionDenied,
    ValidationError,
)

from .firebase import FirebaseHelper

logger = logging.getLogger(__name__)


def auth_request_firebase(request, allow_anonymous=False) -> Tuple[dict, UserRecord]:
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
            token_data, user = firestore.authenticate(token)
            if not allow_anonymous and not user.provider_data:
                raise NotAuthenticated("Anonymous users are not allowed")
            return token_data, user
    except Exception as e:
        if isinstance(e, NotAuthenticated):
            raise e
        logger.warning(e)
        raise AuthenticationFailed(detail="invalid firebase authentication header")


def auth_request_external_oidc(request) -> Tuple[dict, UserRecord]:
    """
    Authenticate external forwarded oidc tokens (e.g. oath2 tokens)
    Args:
        request (Request): DRF request
    """
    try:
        if os.getenv("ASOMAS_SERVER_MODE", "").lower() in ["local", "test"]:
            if "Authorization" in request.headers:
                token = request.headers["Authorization"].split(" ").pop()
            else:
                # {"email": "fielder-emulator@appspot.gserviceaccount.com"}
                token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJlbWFpbCI6ImZpZWxkZXItZW11bGF0b3JAYXBwc3BvdC5nc2VydmljZWFjY291bnQuY29tIn0.PRDpQejYLbKTSrkXsq_LxjF_u_LeeQJpKB_1o1h7jqo"
            return jwt.decode(token, options={"verify_signature": False})
        else:
            if "X-Forwarded-Authorization" in request.headers:
                token = request.headers["X-Forwarded-Authorization"].split(" ").pop()
            else:
                raise AuthenticationFailed(
                    detail="forwarded authorization header not found!"
                )
            req = google.auth.transport.requests.Request()
            return google.oauth2.id_token.verify_oauth2_token(token, req)
    except Exception as e:
        logger.warning(e)
        raise AuthenticationFailed(detail="invalid oidc authorization header")


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


def auth(
    firebase: bool = True, oidc: bool = True, external_oidc=False, allow_anonymous=False
):
    """
    Auth decorator that supports firebase and OIDC token

    Args:
        firebase (bool): if True, authenticate firebase token
        oidc (bool): if True, authenticate OIDC token
        external_oidc (bool): if True, authenticate external forwarded OIDC token
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
                _, req.firebase_user = auth_request_firebase(req, allow_anonymous)
            if oidc:
                req.oidc_data = auth_request_oidc(req)
            if external_oidc:
                req.oidc_data = auth_request_external_oidc(req)

            # run req_handler
            return req_handler(*args, **kwargs)

        return wrapper

    return decorator


def authorize(
    payload_data: dict,
    organisation_user_id: str,
    org_roles: List[str],
    group_roles: List[str] = [],
):
    db = FirebaseHelper.getInstance().db

    organisation_id = payload_data.get("organisation_id")
    if not organisation_id:
        raise ValidationError({"organisation_id": ["This field is required."]})

    # Read from organisation_user_relations collection
    org_user_relation = (
        db.collection("organisation_user_relations")
        .document(f"{organisation_id}_{organisation_user_id}")
        .get()
    )

    if not org_user_relation.exists:
        raise PermissionDenied()

    org_role = org_user_relation.to_dict().get("org_role")

    if org_role not in org_roles:
        raise PermissionDenied()

    if org_role == "GROUP_USER":
        group_id = payload_data.get("group_id")
        if not group_id:
            raise ValidationError({"group_id": ["This field is required."]})

        # Read from group_org_user_relations collection
        group_org_user_relation = (
            db.collection("group_org_user_relations")
            .document(f"{organisation_id}_{group_id}_{organisation_user_id}")
            .get()
        )

        if not group_org_user_relation.exists:
            raise PermissionDenied()

        group_role = group_org_user_relation.to_dict().get("group_role")

        if group_role not in group_roles:
            raise PermissionDenied()


def auth_org_user(
    *,
    firebase: bool,
    oidc: bool,
    org_roles: List[str],
    group_roles: List[str] = [],
    allow_anonymous: bool = False,
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
                data, req.firebase_user = auth_request_firebase(req, allow_anonymous)
                payload_data = {
                    "organisation_id": kwargs.get("organisation_id")
                    or req.data.get("organisation_id"),
                    "group_id": kwargs.get("group_id") or req.data.get("group_id"),
                }
                if (
                    kwargs.get("organisation_id") is not None
                    and req.data.get("organisation_id") is not None
                    and kwargs.get("organisation_id") != req.data.get("organisation_id")
                ):
                    raise PermissionDenied("organisation_id mismatch")
                if (
                    kwargs.get("group_id") is not None
                    and req.data.get("group_id") is not None
                    and kwargs.get("group_id") != req.data.get("group_id")
                ):
                    raise PermissionDenied("group_id mismatch")

                authorize(
                    payload_data,
                    req.firebase_user.uid,
                    org_roles,
                    group_roles=group_roles,
                )

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
