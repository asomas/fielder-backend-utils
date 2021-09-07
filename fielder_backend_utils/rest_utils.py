from django.utils.translation import gettext_lazy as _
from google.cloud.firestore import DocumentReference, GeoPoint
from rest_framework import status
from rest_framework.exceptions import APIException
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


class GeoPointField(Field):
    """
    A field that converts GeoPoint from and to JSON representation.

    The field's incoming value can either be a Firestore GeoPoint,
    or a dict with lat and lng keys:
    {
        "lat": 1.23,
        "lng": 4.56
    }
    """

    default_error_messages = {
        "invalid": "Must be a valid GeoPoint object or a JSON with lat and lng fields.",
    }

    def to_internal_value(self, data):
        if not isinstance(data, GeoPoint):
            if not "lat" in data or not "lng" in data:
                self.fail("invalid", value=data)
            return GeoPoint(data["lat"], data["lng"])
        return data

    # this mehtod changes the serializer.data and not the serializer.validated_data
    def to_representation(self, value):
        return {
            "lat": value.latitude,
            "lng": value.longitude,
        }


class CustomJSONEncoder(JSONEncoder):
    def default(self, obj):
        if isinstance(obj, DocumentReference):
            return str(obj.path)
        if isinstance(obj, GeoPoint):
            return {"lat": obj.latitude, "lng": obj.longitude}
        return super().default(obj)


class Conflict(APIException):
    status_code = status.HTTP_409_CONFLICT
    default_detail = _("Conflict.")


class CustomJSONRenderer(JSONRenderer):
    encoder_class = CustomJSONEncoder
