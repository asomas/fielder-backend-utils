from typing import List

import requests
from requests.models import Response


class ClickUpTask:
    allowed_fields = ["name", "description", "markdown_description", "custom_fields"]

    def __init__(
        self,
        *,
        name: str,
        description: str = None,
        markdown_description: str = None,
        custom_fields: List[dict] = None,
    ) -> None:
        self.name = name
        self.description = description
        self.markdown_description = markdown_description
        self.custom_fields = custom_fields

    def to_dict(self) -> dict:
        return {
            key: value
            for key, value in self.__dict__.items()
            if key in self.allowed_fields
        }


class ClickUpAPIHelper:
    def __init__(self, *, access_token: str) -> None:
        self.base_url = "https://api.clickup.com/api/v2"
        self.access_token = access_token

    def create_task(self, *, list_id: int, task: ClickUpTask) -> Response:
        return requests.post(
            self.base_url + f"/list/{list_id}/task",
            json=task.to_dict(),
            headers={"Authorization": self.access_token},
        )
