from google.cloud.firestore import DocumentReference
from rest_framework.fields import Field
from rest_framework.renderers import JSONRenderer
from rest_framework.utils.encoders import JSONEncoder

from .firebase import FirebaseHelper


class DocumentReferenceField(Field):
    default_error_messages = {
        "invalid": "Must be a valid firestore DocumentReference.",
    }

    def to_internal_value(self, data):
        if not isinstance(data, DocumentReference):
            try:
                if len(data.split("/")) == 2:
                    return FirebaseHelper.getInstance().db.document(data)
                else:
                    self.fail("invalid", value=data)
            except (ValueError):
                self.fail("invalid", value=data)
        return data

    def to_representation(self, value):
        return value.path


class CustomJSONEncoder(JSONEncoder):
    def default(self, obj):
        if isinstance(obj, DocumentReference):
            return str(obj.path)
        return super().default(obj)


class CustomJSONRenderer(JSONRenderer):
    encoder_class = CustomJSONEncoder
