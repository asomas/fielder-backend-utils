from google.cloud.firestore import DocumentReference
from rest_framework.renderers import JSONRenderer
from rest_framework.utils.encoders import JSONEncoder


class CustomJSONEncoder(JSONEncoder):
    def default(self, obj):
        if isinstance(obj, DocumentReference):
            return str(obj.path)
        return super().default(obj)


class CustomJSONRenderer(JSONRenderer):
    encoder_class = CustomJSONEncoder
