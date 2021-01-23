import os
import threading
import firebase_admin
import google.auth.credentials
from datetime import datetime, timezone, timedelta
from firebase_admin import firestore, auth
from google.cloud.firestore_v1 import document, transaction, collection, field_path

import logging

logger = logging.getLogger(__name__)


class FirebaseHelper:
    """
    Singleton Firestore helper
    """

    _instance = None

    @staticmethod
    def getInstance(db=None):
        if FirebaseHelper._instance is None:
            with threading.Lock():
                if FirebaseHelper._instance is None:
                    FirebaseHelper._instance = FirebaseHelper(db)
        return FirebaseHelper._instance

    def __init__(self, db=None):
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
        self.db = db

    def authenticate(self, id_token: str) -> auth.UserRecord:
        """
        Verify id_token and retrieve user info
        """
        decoded_token = auth.verify_id_token(id_token)
        uid = decoded_token["uid"]
        return auth.get_user(uid)
