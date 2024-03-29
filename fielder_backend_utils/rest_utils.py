from enum import Enum
from logging import Logger

import requests
from django.utils.translation import gettext_lazy as _
from google.cloud.firestore import DocumentReference, GeoPoint
from lxml.html.clean import Cleaner
from lxml.html.defs import safe_attrs
from rest_framework import status
from rest_framework.exceptions import APIException
from rest_framework.fields import CharField, ChoiceField, EmailField, Field
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
                if len(data.split("/")) % 2 == 0:
                    return FirebaseHelper.getInstance().db.document(data)
                else:
                    self.fail("invalid", value=data)
            except (ValueError):
                self.fail("invalid", value=data)
        return data

    def to_representation(self, value):
        return value.path


class EnumChoiceField(ChoiceField):
    error_messages = {
        "invalid_enum_class": "enum must be a subclass of builtin Enum class",
    }

    def __init__(self, enum: Enum, **kwargs):
        if not issubclass(enum, Enum):
            return self.fail("invalid_enum_class")
        self.enum = enum
        super().__init__(enum._member_names_, **kwargs)

    def to_internal_value(self, data):
        return self.enum[super().to_internal_value(data)]

    def to_representation(self, value):
        return value.name


class LowercaseEmailField(EmailField):
    def to_internal_value(self, data):
        return super().to_internal_value(data.lower())


class RefToIDField(Field):
    default_error_messages = {
        "invalid": ("value is not a valid reference"),
    }

    def to_internal_value(self, data):
        if isinstance(data, DocumentReference):
            return data.id
        else:
            try:
                if len(data.split("/")) > 1:
                    return data.split("/").pop()
                else:
                    self.fail("invalid", value=data)
            except (ValueError):
                self.fail("invalid", value=data)


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


def log_response(logger: Logger, response: requests.Response, payload: dict = None):
    try:
        message = response.json()
    except ValueError:
        message = response.text
    if 600 > response.status_code >= 400:
        logger.error(
            f"{response.status_code} error while connecting to {response.url}! payload={str(payload)} reason={response.reason}, message = {message}"
        )


class CleanHTMLField(CharField):
    def to_internal_value(self, data):
        data = super().to_internal_value(data)
        return Cleaner(
            scripts=True,
            safe_attrs=safe_attrs | set(["style"]),
        ).clean_html(data)
