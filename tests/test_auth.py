from unittest import TestCase, mock
from fielder_backend_utils import auth

class TestAuth(TestCase):
    @mock.patch('fielder_backend_utils.auth.FirebaseHelper')
    def test_auth_request_firebase(self, FirebaseHelperMock):
        firebase_mock = mock.Mock()
        firebase_mock.authenticate.return_value = mock.Mock(uid='TEST_USER_UID')
        FirebaseHelperMock.getInstance.return_value = firebase_mock        

        # no authorization header
        request = mock.Mock()
        request.headers = {"X-Someting-Else": "something-else"}
        self.assertRaises(RuntimeError, auth.auth_request_firebase, request)

        # X-Forwarded-Authorization
        request = mock.Mock()
        request.headers = {"X-Forwarded-Authorization": "Bearer FIREBASE_TOKEN"}
        user = auth.auth_request_firebase(request)
        self.assertEqual(user.uid, 'TEST_USER_UID')

        # Authorization
        request = mock.Mock()
        request.headers = {"Authorization": "Bearer FIREBASE_TOKEN"}
        user = auth.auth_request_firebase(request)
        self.assertEqual(user.uid, 'TEST_USER_UID')

    @mock.patch('fielder_backend_utils.auth.google')
    def test_auth_request_oidc(self, google_mock):
        google_mock.auth.transport.requests.Request.return_value = mock.Mock()
        google_mock.oauth2.id_token.verify_oauth2_token.return_value = {
            'email': 'fielder@appspot.gserviceaccount.com'}

        # no authorization header
        request = mock.Mock()
        request.headers = {"X-Someting-Else": "something-else"}
        self.assertRaises(RuntimeError, auth.auth_request_oidc, request)

        # Authorization
        request = mock.Mock()
        request.headers = {"Authorization": "Bearer OIDC_TOKEN"}
        token_data = auth.auth_request_oidc(request)
        self.assertEqual(token_data['email'], 'fielder@appspot.gserviceaccount.com')
