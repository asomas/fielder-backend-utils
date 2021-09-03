import requests
from requests.models import HTTPError


class IntercomClient:
    """
    API DOCS: https://developers.intercom.com/intercom-api-reference/reference
    """

    def __init__(self, access_token: str):
        self.headers = {"Authorization": "Bearer " + access_token}

    def get_user(self, external_user_id: str) -> list[dict]:
        # Try to search a user by external_id i.e. Firestore document ID
        response = requests.post(
            "https://api.intercom.io/contacts/search",
            json={
                "query": {
                    "field": "external_id",
                    "operator": "=",
                    "value": external_user_id,
                }
            },
            headers=self.headers,
        )
        if response.status_code == 200:
            return response.json()["data"]

        return response.raise_for_status()

    def create_user(self, external_user_id: str, **kwargs) -> dict:
        payload = {
            "role": "user",
            "external_id": external_user_id,
        }
        if kwargs:
            payload.update(kwargs)

        response = requests.post(
            "https://api.intercom.io/contacts",
            json=payload,
            headers=self.headers,
        )
        if response.status_code == 200:
            return response.json()
        return response.raise_for_status()

    def get_or_create_user(self, external_user_id: str, **kwargs) -> dict:
        try:
            user = self.get_user(external_user_id)[0]
        except HTTPError as e:
            if e.response.status_code == 404:
                user = self.create_user(external_user_id, **kwargs)
            else:
                raise e
        return user

    def update_user(self, intercom_user_id: str, **kwargs) -> dict:
        payload = {}
        if kwargs:
            payload.update(kwargs)

        response = requests.put(
            "https://api.intercom.io/contacts/{}".format(intercom_user_id),
            json=payload,
            headers=self.headers,
        )
        if response.status_code == 200:
            return response.json()
        return response.raise_for_status()

    def get_company(self, organisation_id: str) -> dict:
        response = requests.get(
            f"https://api.intercom.io/companies/{organisation_id}",
            headers=self.headers,
        )
        if response.status_code == 200:
            return response.json()

        return response.raise_for_status()

    def create_update_company(self, organisation_id: str, **kwargs) -> dict:
        payload = {
            "name": organisation_id,
        }
        if kwargs:
            payload.update(kwargs)

        response = requests.post(
            "https://api.intercom.io/companies",
            json=payload,
            headers=self.headers,
        )
        if response.status_code == 200:
            return response.json()

        return response.raise_for_status()

    def add_user_to_company(
        self, intercom_user_id: str, intercom_company_id: str
    ) -> dict:
        response = requests.post(
            f"https://api.intercom.io/contacts/{intercom_user_id}/companies",
            json={"id": intercom_company_id},
            headers=self.headers,
        )
        if response.status_code == 200:
            return response.json()
        return response.raise_for_status()

    def create_conversation(self, intercom_user_id: str, body: str) -> dict:
        response = requests.post(
            "https://api.intercom.io/conversations",
            json={
                "from": {"type": "user", "id": intercom_user_id},
                "body": body,
            },
            headers=self.headers,
        )
        if response.status_code == 200:
            return response.json()

        return response.raise_for_status()
