from fielder_backend_utils import get_with_default
from typing import Any, Dict, OrderedDict
from google.cloud.firestore import DocumentReference, GeoPoint
import requests


def google_place_details(
    place_id: str, googel_places_api_secret: str
) -> Dict[str, Any]:
    response = requests.get(
        "https://maps.googleapis.com/maps/api/place/details/json",
        params={
            "place_id": place_id,
            "key": googel_places_api_secret,
        },
    ).json()

    if response["status"] == "OK":
        name = response["result"]["name"]
        info = response["result"]["address_components"]
        building = [
            _["long_name"]
            for _ in info
            if "street_number" in _["types"] or "premise" in _["types"]
        ]
        street = [_["long_name"] for _ in info if "route" in _["types"]]
        city = [_["long_name"] for _ in info if "postal_town" in _["types"]]
        administrative_areas_names = [
            _["long_name"] for _ in info if "administrative_area_level_2" in _["types"]
        ] + [
            _["long_name"] for _ in info if "administrative_area_level_1" in _["types"]
        ]
        country = [_["long_name"] for _ in info if "country" in _["types"]]
        postal_code = [_["long_name"] for _ in info if "postal_code" in _["types"]]

        return {
            "name": name,
            "address": {
                "building": building[0] if building else None,
                "street": street[0] if street else None,
                "city": city[0] if city else None,
                "county": ", ".join(administrative_areas_names)
                if administrative_areas_names
                else None,
                "country": country[0] if country else None,
                "postal_code": postal_code[0] if postal_code else None,
            },
            "coords": response["result"]["geometry"]["location"],
            "formatted_address": response["result"]["formatted_address"],
        }
    else:
        return None


def generate_location(
    loc_data: Dict[str, Any], organisation_ref: DocumentReference
) -> Dict[str, Any]:
    """
    Generate location data

    Args:
        loc_data: initial location data
        organisation_ref: organisation document reference
    Returns:
        loc_data: location data
    """
    c = loc_data["coords"]
    loc_data["coords"] = GeoPoint(c["lat"], c["lng"])
    loc_data["organisation_ref"] = organisation_ref
    loc_data["archived"] = False
    loc_data["is_live"] = True
    short_name = (
        loc_data.get("name")
        if get_with_default(loc_data, "name", None) is not None
        else f"{get_with_default(loc_data['address'], 'building', '')} {get_with_default(loc_data['address'], 'street', '')}".strip()
    )
    loc_data["short_name"] = short_name
    loc_data["icon_url"] = None  # TODO

    # Order the keys to create formatted_address
    order_of_keys = ["building", "street", "city", "county", "postal_code", "country"]
    loc_data["address"] = OrderedDict(
        [(key, loc_data["address"][key]) for key in order_of_keys]
    )
    formatted_address = ", ".join([v for k, v in loc_data["address"].items() if v])
    loc_data["formatted_address"] = (
        formatted_address if formatted_address else loc_data["formatted_address"]
    )

    return loc_data