from datetime import datetime

import requests
from google.cloud.firestore_v1.client import Client


def get_sic_code_description(db, code):
    sic_code_snapshot = db.collection("sic_codes").document(code).get()

    if sic_code_snapshot.exists:
        return sic_code_snapshot.to_dict().get("description", None)
    return None


def get_directors(api_key, company_number):
    officers_response = requests.get(
        f"https://api.company-information.service.gov.uk/company/{company_number}/officers",
        auth=(api_key, ""),
    )

    if officers_response.status_code == 200:

        directors = [
            {
                "name": item["name"],
                "appointment_date": datetime.strptime(item["appointed_on"], "%Y-%m-%d"),
            }
            for item in officers_response.json()["items"]
            if "resigned_on" not in item
        ]

        return directors


def get_last_filing_date(api_key, company_number):
    filing_history_response = requests.get(
        f"https://api.company-information.service.gov.uk/company/{company_number}/filing-history",
        auth=(api_key, ""),
    )

    if filing_history_response.status_code == 200:
        items = filing_history_response.json()["items"]
        if items:
            date = items[0].get("date")
            if date:
                return datetime(*[int(_) for _ in date.split("-")])


def get_company_data(
    api_key,
    company_number,
    db=None,
    sic_codes=True,
    directors=True,
    filing_history=True,
):
    company_data = {}
    response = requests.get(
        f"https://api.company-information.service.gov.uk/company/{company_number}",
        auth=(api_key, ""),
    )
    if response.status_code == 200:
        response_data = response.json()
        company_data["company_name"] = response_data.get("company_name")
        company_data["last_updated"] = datetime.now()
        company_data["incorporation_date"] = datetime.strptime(
            response_data["date_of_creation"], "%Y-%m-%d"
        )
        company_data["registration_number"] = response_data.get("company_number")
        company_data["directors"] = []
        company_data["sic_codes"] = []
        company_data["last_filing_date"] = None

        # SIC Codes
        if sic_codes:
            assert isinstance(
                db, Client
            ), "Access to database is required to get SIC Codes"
            company_data["sic_codes"] = (
                [
                    {
                        "code": code,
                        "description": get_sic_code_description(db, code),
                    }
                    for code in response_data["sic_codes"]
                ]
                if response_data.get("sic_codes", None)
                else []
            )

        # Address
        if response_data.get("registered_office_address", None):
            company_data["address"] = {
                "name": response_data["registered_office_address"].get(
                    "address_line_1", None
                ),
                "street": response_data["registered_office_address"].get(
                    "address_line_2", None
                ),
                "town": response_data["registered_office_address"].get(
                    "locality", None
                ),
                "county": response_data["registered_office_address"].get(
                    "region", None
                ),
                "country": response_data["registered_office_address"].get(
                    "country", None
                ),
                "postcode": response_data["registered_office_address"].get(
                    "postal_code", None
                ),
                "po_box": None,
            }

        # Directors
        if directors:
            company_data.update({"directors": get_directors(api_key, company_number)})

        # Filing History
        if filing_history:
            company_data["last_filing_date"] = get_last_filing_date(
                api_key, company_number
            )

    return company_data


def get_company_number(api_key: str, name: str) -> str:
    url = "https://api.company-information.service.gov.uk/search/companies"
    response = requests.get(
        url,
        params={"q": name},
        auth=(api_key, ""),
    )
    data = response.json()
    company_number = None
    items = data.get("items", [])
    if len(items) > 1:
        company = items[0]
        company_number = (
            company["company_number"]
            if company.get("company_status", None)
            not in [
                None,
                "dissolved",
            ]
            else None
        )
    return company_number
