import logging
import os
import threading
from typing import Optional, Tuple

import firebase_admin
import google.auth.credentials
from firebase_admin import auth, firestore
from firebase_admin.auth import (
    UserNotFoundError,
    UserRecord,
    create_user,
    get_user,
    get_user_by_phone_number,
)
from google.cloud.firestore import Client

logger = logging.getLogger(__name__)


class FirebaseHelper:
    """
    Singleton Firestore helper
    """

    _instance = None

    @staticmethod
    def getInstance(db: Client = None):
        if FirebaseHelper._instance is None:
            with threading.Lock():
                if FirebaseHelper._instance is None:
                    FirebaseHelper._instance = FirebaseHelper(db)
        return FirebaseHelper._instance

    def __init__(self, db: Client = None):
        if not db:
            if os.getenv("FIRESTORE_PROJECT_ID") and os.getenv(
                "FIRESTORE_EMULATOR_HOST"
            ):
                # Use emulator
                from unittest import mock

                cred = mock.Mock(spec=google.auth.credentials.Credentials)
                db = firestore.Client(
                    project=os.environ.get("FIRESTORE_PROJECT_ID"), credentials=cred
                )
            else:
                # if no credential passed as argument,
                # the sdk will first search env var GOOGLE_APPLICATION_CREDENTIALS
                # that should contain absolute path to JSON credential file (can be used in local),
                # or it will use default service account for the App Engine instance
                if not firebase_admin._apps:
                    firebase_admin.initialize_app()
                db = firestore.client()
        self.db = db  # type: Client

    def authenticate(self, id_token: str) -> Tuple[dict, auth.UserRecord]:
        """
        Verify id_token and retrieve user info
        """
        data = auth.verify_id_token(id_token)
        return (data, auth.get_user(data["uid"]))


class FirebaseAuthService:
    def __init__(self) -> None:
        FirebaseHelper().getInstance()

    def user_exists(self, *, uid: str) -> bool:
        try:
            get_user(uid)
            return True
        except UserNotFoundError:
            return False

    def user_exists_via_phone(self, *, phone_number: str) -> bool:
        try:
            get_user_by_phone_number(phone_number)
            return True
        except UserNotFoundError:
            return False

    def get_last_login(self, *, user_id: str) -> Optional[int]:
        try:
            user: UserRecord = get_user(user_id)
            return user.user_metadata.last_sign_in_timestamp
        except UserNotFoundError:
            pass

    def create_user(self, *, phone_number: str, display_name: str = None) -> UserRecord:
        kwargs = {"phone_number": phone_number}
        if display_name != None:
            kwargs["display_name"] = display_name
        return create_user(**kwargs)
