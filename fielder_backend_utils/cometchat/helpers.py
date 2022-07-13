from typing import Optional

import requests
from requests import Response

from .dataclasses import CometChatAuthToken, CometChatUser
from .enums import CometChatErrorCodes
from .exceptions import (
    CometChatAuthTokenNotFoundException,
    CometChatException,
    CometChatUIDAlreadyExistsException,
    CometChatUIDNotFoundException,
)


class CometChatHelper:
    def __init__(self, app_id: str, region: str, api_key: str) -> None:
        self.base_url = f"https://{app_id}.api-{region}.cometchat.io/v3"
        self.default_headers = {
            "apiKey": f"{api_key}",
            "Content-Type": "application/json",
            "Accept": "application/json",
        }

    def create_user(
        self,
        uid: str,
        name: str,
        avatar: Optional[str] = None,
        link: Optional[str] = None,
        role: Optional[str] = None,
        metadata: Optional[str] = None,
        with_auth_token: Optional[bool] = None,
        tags: Optional[list[str]] = None,
    ) -> CometChatUser:
        payload = {}

        payload["uid"] = uid
        payload["name"] = name

        if avatar:
            payload["avatar"] = avatar
        if link:
            payload["link"] = link
        if role:
            payload["role"] = role
        if metadata:
            payload["metadata"] = metadata
        if with_auth_token:
            payload["withAuthToken"] = with_auth_token
        if tags:
            payload["tags"] = tags

        response = requests.post(
            self.base_url + "/users", json=payload, headers=self.default_headers
        )

        if not response.ok:
            self._handle_bad_request(response)

        return CometChatUser(**response.json()["data"])

    def get_user(self, uid: str) -> CometChatUser:
        response = requests.get(
            self.base_url + f"/users/{uid}", headers=self.default_headers
        )

        if not response.ok:
            self._handle_bad_request(response)

        return CometChatUser(**response.json()["data"])

    def update_user(
        self,
        uid: str,
        name: Optional[str] = None,
        avatar: Optional[str] = None,
        link: Optional[str] = None,
        role: Optional[str] = None,
        metadata: Optional[str] = None,
        tags: Optional[list[str]] = None,
    ) -> CometChatUser:
        payload = {}

        if name:
            payload["name"] = name
        if avatar:
            payload["avatar"] = avatar
        if link:
            payload["link"] = link
        if role:
            payload["role"] = role
        if metadata:
            payload["metadata"] = metadata
        if tags:
            payload["tags"] = tags

        response = requests.put(
            self.base_url + f"/users/{uid}", json=payload, headers=self.default_headers
        )

        if not response.ok:
            self._handle_bad_request(response)

        return CometChatUser(**response.json()["data"])

    def delete_user(self, uid: str, permanent: bool = True) -> None:
        response = requests.delete(
            self.base_url + f"/users/{uid}",
            json={"permanent": permanent},
            headers=self.default_headers,
        )

        if not response.ok:
            self._handle_bad_request(response)

    def create_auth_token(self, uid: str, force: bool = False) -> CometChatAuthToken:
        response = requests.post(
            self.base_url + f"/users/{uid}/auth_tokens",
            json={"force": force},
            headers=self.default_headers,
        )

        if not response.ok:
            self._handle_bad_request(response)

        return CometChatAuthToken(**response.json()["data"])

    def get_auth_token(self, uid: str, auth_token: str) -> CometChatAuthToken:
        response = requests.get(
            self.base_url + f"/users/{uid}/auth_tokens/{auth_token}",
            headers=self.default_headers,
        )

        if not response.ok:
            self._handle_bad_request(response)

        return CometChatAuthToken(**response.json()["data"])

    def _handle_bad_request(self, response: Response) -> None:
        code = response.json()["error"]["code"]
        message = response.json()["error"]["message"]

        if code == CometChatErrorCodes.ERR_UID_ALREADY_EXISTS.name:
            raise CometChatUIDAlreadyExistsException(message)

        elif code == CometChatErrorCodes.ERR_UID_NOT_FOUND.name:
            raise CometChatUIDNotFoundException(message)

        elif code == CometChatErrorCodes.ERR_AUTH_TOKEN_NOT_FOUND.name:
            raise CometChatAuthTokenNotFoundException(message)

        else:
            raise CometChatException(response.text)