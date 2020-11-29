import os
import functools
import google.oauth2.id_token
import google.auth.transport.requests
from typing import Tuple, Dict
from firebase_admin.auth import UserRecord
from .firebase import FirebaseHelper

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
        return firestore.authenticate(token)
    except Exception as e:
        logger.warning(e)
        raise RuntimeError('invalid firebase authentication header')

def auth_request_oidc(request) -> dict:
    """
    Authenticate oidc id_token and get jwt info as dict
    Args:
        request (Request): DRF request
    Returns:
        data (dict): data from token
    """
    try:
        token = request.headers["Authorization"].split(" ").pop()
        req = google.auth.transport.requests.Request()
        return google.oauth2.id_token.verify_oauth2_token(token, req)
    except Exception as e:
        logger.warning(e)
        raise RuntimeError('invalid oidc authorization header')

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
            # skip on test mode
            if os.getenv('ASOMAS_SERVER_MODE','').lower() == 'test':
                return req_handler(*args, **kwargs)

            # assume request object is one
            # of the args
            req = None
            for arg in args:
                if type(arg).__name__.lower() == 'request':
                    req = arg
                    req.firebase_user = None
                    req.oidc_data = None
                    break
            if not req:
                raise RuntimeError('no rest_framework.request.Request in args')

            # authenticate
            authenticated = not (firebase or oidc)
            if firebase:
                try:
                    req.firebase_user = auth_request_firebase(req)
                    authenticated = True
                except Exception as e:
                    print(e)
                    pass
            if oidc:
                try:
                    req.oidc_data = auth_request_oidc(req)
                    authenticated = True
                except Exception as e:
                    print(e)
                    pass
            if not authenticated:
                raise RuntimeError('invalid firebase & oidc authorization header')
            
            # run req_handler
            return req_handler(*args, **kwargs)
        return wrapper
    return decorator