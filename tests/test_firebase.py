from unittest import TestCase, mock
from fielder_backend_utils.firebase import FirebaseHelper


class TestFirebase(TestCase):
    @mock.patch("fielder_backend_utils.firebase.firestore")
    @mock.patch("fielder_backend_utils.firebase.firebase_admin")
    def test_firebase_helper(self, firebase_admin_mock, firestore_mock):
        firebase_admin_mock._apps = None
        firebase_admin_mock.initialize_app.return_value = None
        db_mock = mock.Mock()
        firestore_mock.client.return_value = db_mock
        firebase1 = FirebaseHelper.getInstance()
        firebase2 = FirebaseHelper.getInstance()
        # test if singleton works
        firebase_admin_mock.initialize_app.assert_called_once()
