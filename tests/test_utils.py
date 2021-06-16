from unittest import TestCase
from google.cloud.firestore import GeoPoint
from fielder_backend_utils import (
    generate_location,
    get_with_default,
    make_chunks,
)


class TestUtils(TestCase):
    def test_make_chunks(self):
        n = 10
        c = 3
        l = list(range(n))
        i = 0
        for chunk in make_chunks(l, c):
            start = i * c
            end = min((i + 1) * c, n)
            self.assertEqual(chunk, list(range(start, end)))
            i = i + 1

    def test_get_with_default(self):
        test_data = {"one": "1", "two": None}

        self.assertEqual(get_with_default(test_data, "one", "1"), "1")
        self.assertEqual(get_with_default(test_data, "two", "2"), "2")
        self.assertEqual(get_with_default(test_data, "three", "3"), "3")

    def test_generate_locaiton(self):
        initial_location = {
            "address": {
                "building": "building",
                "street": None,
                "city": "city",
                "county": "county",
                "country": "country",
                "postal_code": "postal_code",
            },
            "coords": {"lat": "1", "lng": "2"},
        }

        expected_location = {
            "address": {
                "building": "building",
                "street": None,
                "city": "city",
                "county": "county",
                "postal_code": "postal_code",
                "country": "country",
            },
            "coords": GeoPoint("1", "2"),
            "organisation_ref": None,
            "archived": False,
            "is_live": True,
            "short_name": "building",
            "icon_url": None,
            "formatted_address": "building, city, county, postal_code, country",
        }
        location_data = generate_location(initial_location, None)
        self.assertDictEqual(location_data, expected_location)

        initial_location = {
            "name": "name",
            "address": {
                "building": "building",
                "street": "street",
                "city": "city",
                "county": "county",
                "country": "country",
                "postal_code": "postal_code",
            },
            "coords": {"lat": "1", "lng": "2"},
        }

        expected_location = {
            "name": "name",
            "address": {
                "building": "building",
                "street": "street",
                "city": "city",
                "county": "county",
                "country": "country",
                "postal_code": "postal_code",
            },
            "coords": GeoPoint("1", "2"),
            "organisation_ref": None,
            "archived": False,
            "is_live": True,
            "short_name": "name",
            "icon_url": None,
            "formatted_address": "building, street, city, county, postal_code, country",
        }
        location_data = generate_location(initial_location, None)
        self.assertDictEqual(location_data, expected_location)
