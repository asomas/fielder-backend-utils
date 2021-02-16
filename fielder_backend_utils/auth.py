import os
import jwt
import functools
import google.oauth2.id_token
import google.auth.transport.requests
from typing import Tuple, Dict
from .firebase import FirebaseHelper
from firebase_admin.auth import UserRecord
from rest_framework.exceptions import AuthenticationFailed
from unittest import mock

import logging

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
