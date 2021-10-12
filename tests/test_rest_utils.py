from unittest.case import TestCase

import django
from django.conf import settings

if not settings.configured:
    settings.configure()
    django.setup()

from fielder_backend_utils.rest_utils import GeoPointField
from google.cloud.firestore import GeoPoint
from rest_framework import serializers


class GeoPointTestSerializer(serializers.Serializer):
    name = serializers.CharField()
    point = GeoPointField()


class TestShift(TestCase):
    def test_geopoint_field(self):

        data = {"name": "test", "point": {"lat": 1.0, "lng": 2.0}}
        serializer = GeoPointTestSerializer(data=data)
        serializer.is_valid(raise_exception=True)
        # we assert against serializer.data to get the representation data
        self.assertDictEqual(data, serializer.data)

        data2 = {"name": "test", "point": GeoPoint(1.0, 2.0)}
        serializer = GeoPointTestSerializer(data=data2)
        serializer.is_valid(raise_exception=True)
        # we assert against serializer.validated_data to get the internal data
        self.assertDictEqual(data2, serializer.validated_data)
