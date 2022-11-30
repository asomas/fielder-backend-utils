import os
from unittest import TestCase, mock

import jwt
from rest_framework.exceptions import AuthenticationFailed

from fielder_backend_utils import auth


class TestAuth(TestCase):
    @mock.patch("fielder_backend_utils.auth.FirebaseHelper")
    def test_auth_request_firebase(self, FirebaseHelperMock):
        firebase_mock = mock.Mock()
        firebase_mock.authenticate.return_value = ({}, mock.Mock(uid="TEST_USER_UID"))
        FirebaseHelperMock.getInstance.return_value = firebase_mock

        # no authorization header
        request = mock.Mock()
        request.headers = {"X-Someting-Else": "something-else"}
        self.assertRaises(AuthenticationFailed, auth.auth_request_firebase, request)

        # X-Forwarded-Authorization
        request = mock.Mock()
        request.headers = {"X-Forwarded-Authorization": "Bearer FIREBASE_TOKEN"}
        _, user = auth.auth_request_firebase(request)
        self.assertEqual(user.uid, "TEST_USER_UID")

        # Authorization
        request = mock.Mock()
        request.headers = {"Authorization": "Bearer FIREBASE_TOKEN"}
        _, user = auth.auth_request_firebase(request)
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

    @mock.patch("fielder_backend_utils.auth.google")
    def test_auth_request_external_oidc(self, google_mock):
        google_mock.auth.transport.requests.Request.return_value = mock.Mock()
        google_mock.oauth2.id_token.verify_oauth2_token.return_value = {
            "email": "fielder@appspot.gserviceaccount.com"
        }

        # no authorization header
        request = mock.Mock()
        request.headers = {"X-Someting-Else": "something-else"}
        self.assertRaises(
            AuthenticationFailed, auth.auth_request_external_oidc, request
        )

        # no forwarded header
        request = mock.Mock()
        request.headers = {"Authorization": "Bearer OIDC_TOKEN"}
        self.assertRaises(
            AuthenticationFailed, auth.auth_request_external_oidc, request
        )

        # Authorization
        request = mock.Mock()
        request.headers = {"X-Forwarded-Authorization": "Bearer FIREBASE_TOKEN"}
        token_data = auth.auth_request_external_oidc(request)
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
        _, user = auth.auth_request_firebase(request)
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

    @mock.patch("fielder_backend_utils.auth.FirebaseHelper")
    @mock.patch("google.oauth2.id_token.verify_oauth2_token")
    def test_auth_decorator(self, verify_oauth2_token_mock, FirebaseHelperMock):
        # mock
        firebase_mock = mock.Mock()
        firebase_mock.authenticate.return_value = ({}, mock.Mock(uid="TEST_USER_UID"))
        FirebaseHelperMock.getInstance.return_value = firebase_mock

        # dummy request
        class Request:
            def __init__(self):
                self.headers = {}

        # no auth
        @auth.auth(firebase=False, oidc=False)
        def func1(r):
            return r

        req = Request()
        res = func1(req)
        self.assertEqual(res, req)

        # oidc only
        @auth.auth(firebase=False)
        def func2(r):
            return r

        # reject if no token
        self.assertRaises(AuthenticationFailed, func2, Request())

        # accept if there is a token
        oidc_payload = {
            "email": "test@email.com",
        }
        oidc_token = jwt.encode(oidc_payload, key="secret", algorithm="HS256")
        req = Request()
        req.headers["Authorization"] = f"Bearer {oidc_token}"
        verify_oauth2_token_mock.return_value = oidc_payload
        res = func2(req)
        self.assertEquals(res.oidc_data, oidc_payload)

        # firebase and oidc
        @auth.auth()
        def func3(r):
            return r

        # reject if only firebase token
        firebase_payload = {
            "user_id": "JpCl3YvRxwMhNao1D3qKuCJltKgy",
            "phone_number": "+1122334455",
            "email": "jane@asomas.com",
        }
        firebase_token = jwt.encode(firebase_payload, key="secret", algorithm="HS256")
        req = Request()
        req.headers["Authorization"] = f"Bearer {firebase_token}"
        # verify_oauth2_token() will reject firebase token
        verify_oauth2_token_mock.side_effect = Exception()
        self.assertRaises(AuthenticationFailed, func3, req)

        # accept if both provided
        req = Request()
        req.headers["X-Forwarded-Authorization"] = f"Bearer {firebase_token}"
        req.headers["Authorization"] = f"Bearer {oidc_token}"
        # firebase.authenticate will return user object
        firebase_mock.authenticate.return_value = (
            {},
            mock.Mock(uid=firebase_payload["user_id"]),
        )
        # verify_oauth2_token() will accept oidc token
        verify_oauth2_token_mock.side_effect = None
        verify_oauth2_token_mock.return_value = oidc_payload
        res = func3(req)
        self.assertEquals(res.oidc_data, oidc_payload)
        self.assertEquals(res.firebase_user.uid, firebase_payload["user_id"])
