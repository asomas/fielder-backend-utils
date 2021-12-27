import requests
from requests.models import Response


class ClickUpTask:
    allowed_fields = ["name", "description"]

    def __init__(
        self,
        *,
        name: str,
        description: str = None,
    ) -> None:
        self.name = name
        self.description = description

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
