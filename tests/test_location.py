from unittest import TestCase, mock

from fielder_backend_utils.location import *

google_palce_api_response = {
    "html_attributions": [],
    "result": {
        "address_components": [
            {"long_name": "50", "short_name": "50", "types": ["street_number"]},
            {
                "long_name": "Kensington Court",
                "short_name": "Kensington Ct",
                "types": ["route"],
            },
            {"long_name": "London", "short_name": "London", "types": ["postal_town"]},
            {
                "long_name": "Greater London",
                "short_name": "Greater London",
                "types": ["administrative_area_level_2", "political"],
            },
            {
                "long_name": "England",
                "short_name": "England",
                "types": ["administrative_area_level_1", "political"],
            },
            {
                "long_name": "United Kingdom",
                "short_name": "GB",
                "types": ["country", "political"],
            },
            {"long_name": "W8 5DB", "short_name": "W8 5DB", "types": ["postal_code"]},
        ],
        "formatted_address": "50 Kensington Ct, London W8 5DB, UK",
        "geometry": {
            "location": {"lat": 51.5019092, "lng": -0.1884173},
            "viewport": {
                "northeast": {"lat": 51.5031765802915, "lng": -0.187067769708498},
                "southwest": {"lat": 51.5004786197085, "lng": -0.189765730291502},
            },
        },
        "icon": "https://maps.gstatic.com/mapfiles/place_api/icons/v1/png_71/geocode-71.png",
        "name": "50 Kensington Ct",
        "place_id": "ChIJZ3N-1PcPdkgRX6EY_V9C9q8",
        "reference": "ChIJZ3N-1PcPdkgRX6EY_V9C9q8",
        "types": ["premise"],
        "url": "https://maps.google.com/?q=50+Kensington+Ct,+London+W8+5DB,+UK&ftid=0x48760ff7d47e7367:0xaff6425ffd18a15f",
        "utc_offset": 60,
    },
    "status": "OK",
}


def mocked_requests_get(*args, **kwargs):
    class MockResponse:
        def __init__(self, json_data, status_code):
            self.json_data = json_data
            self.status_code = status_code
            self.url = args[0]

        def json(self):
            return self.json_data

    if kwargs["params"]["key"] == "API_SECRET":
        if (
            kwargs["params"]["place_id"] == "GOOGLE_PLACE_ID"
            and args[0] == "https://maps.googleapis.com/maps/api/place/details/json"
        ):
            return MockResponse(google_palce_api_response, 200)
        return MockResponse(None, 404)
    return MockResponse(None, 403)


class TestLocation(TestCase):
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

    @mock.patch("requests.get", side_effect=mocked_requests_get)
    def test_google_location_api(self, mock_get):

        expected_location = {
            "name": "50 Kensington Ct",
            "address": {
                "building": "50",
                "street": "Kensington Court",
                "city": "London",
                "county": "Greater London, England",
                "country": "United Kingdom",
                "postal_code": "W8 5DB",
            },
            "coords": {"lat": 51.5019092, "lng": -0.1884173},
            "formatted_address": "50 Kensington Ct, London W8 5DB, UK",
        }
        self.assertDictEqual(
            google_place_details("GOOGLE_PLACE_ID", "API_SECRET"), expected_location
        )
