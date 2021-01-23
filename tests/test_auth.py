import os
import jwt
from unittest import TestCase, mock
from fielder_backend_utils import auth
from rest_framework.exceptions import AuthenticationFailed


class TestAuth(TestCase):
    @mock.patch("fielder_backend_utils.auth.FirebaseHelper")
    def test_auth_request_firebase(self, FirebaseHelperMock):
        firebase_mock = mock.Mock()
        firebase_mock.authenticate.return_value = mock.Mock(uid="TEST_USER_UID")
        FirebaseHelperMock.getInstance.return_value = firebase_mock

        # no authorization header
        request = mock.Mock()
        request.headers = {"X-Someting-Else": "something-else"}
        self.assertRaises(AuthenticationFailed, auth.auth_request_firebase, request)

        # X-Forwarded-Authorization
        request = mock.Mock()
        request.headers = {"X-Forwarded-Authorization": "Bearer FIREBASE_TOKEN"}
        user = auth.auth_request_firebase(request)
        self.assertEqual(user.uid, "TEST_USER_UID")

        # Authorization
        request = mock.Mock()
        request.headers = {"Authorization": "Bearer FIREBASE_TOKEN"}
        user = auth.auth_request_firebase(request)
        self.assertEqual(user.uid, "TEST_USER_UID")

    @mock.patch("fielder_backend_utils.auth.google")
    def test_auth_request_oidc(self, google_mock):
        google_mock.auth.transport.requests.Request.return_value = mock.Mock()
        google_mock.oauth2.id_token.verify_oauth2_token.return_value = {
            "email": "fielder@appspot.gserviceaccount.com"
        }

        # no authorization header
        request = mock.Mock()
        request.headers = {"X-Someting-Else": "something-else"}
        self.assertRaises(AuthenticationFailed, auth.auth_request_oidc, request)

        # Authorization
        request = mock.Mock()
        request.headers = {"Authorization": "Bearer OIDC_TOKEN"}
        token_data = auth.auth_request_oidc(request)
        self.assertEqual(token_data["email"], "fielder@appspot.gserviceaccount.com")

    @mock.patch("fielder_backend_utils.auth.FirebaseHelper")
    def test_auth_request_firebase_local(self, FirebaseHelperMock):
        os.environ["ASOMAS_SERVER_MODE"] = "local"
        payload = {
            "user_id": "JpCl3YvRxwMhNao1D3qKuCJltKgy",
            "phone_number": "+1122334455",
            "email": "jane@asomas.com",
        }
        token = jwt.encode(payload, key="secret", algorithm="HS256")
        request = mock.Mock()
        request.headers = {"Authorization": "Bearer " + token}
        user = auth.auth_request_firebase(request)
        self.assertEqual(user.uid, payload["user_id"])
        self.assertEqual(user.phone_number, payload["phone_number"])
        self.assertEqual(user.email, payload["email"])
        del os.environ["ASOMAS_SERVER_MODE"]

    def test_auth_request_oidc(self):
        os.environ["ASOMAS_SERVER_MODE"] = "local"

        # should accept valid header
        payload = {
            "email": "fielder-dev-285511@appspot.gserviceaccount.com",
        }
        token = jwt.encode(payload, key="secret", algorithm="HS256")
        request = mock.Mock()
        request.headers = {"Authorization": "Bearer " + token}
        token_data = auth.auth_request_oidc(request)
        self.assertDictEqual(token_data, payload)

        # should accept no authentication header
        request = mock.Mock()
        request.headers = {}
        token_data = auth.auth_request_oidc(request)
        self.assertDictEqual(
            token_data, {"email": "fielder-emulator@appspot.gserviceaccount.com"}
        )

        del os.environ["ASOMAS_SERVER_MODE"]
