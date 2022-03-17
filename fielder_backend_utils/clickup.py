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

    def get_task(
        self, task_id: str, custom_task_ids: bool = False, team_id: int = None
    ) -> Response:
        if custom_task_ids == True and team_id is None:
            raise Exception(
                "If you want to reference a task by it's custom task id, team_id must be provided."
            )
        return requests.get(
            self.base_url + f"/task/{task_id}",
            params={"custom_task_ids": custom_task_ids, "team_id": team_id},
            headers={"Authorization": self.access_token},
        )

    def update_task(
        self,
        task_id: str,
        data: dict,
        custom_task_ids: bool = False,
        team_id: int = None,
    ) -> Response:
        if custom_task_ids == True and team_id is None:
            raise Exception(
                "If you want to reference a task by it's custom task id, team_id must be provided."
            )
        return requests.put(
            self.base_url + f"/task/{task_id}",
            params={"custom_task_ids": custom_task_ids, "team_id": team_id},
            headers={"Authorization": self.access_token},
        )

    def set_task_status(
        self,
        task_id: str,
        status: str,
        custom_task_ids: bool = False,
        team_id: int = None,
    ) -> Response:
        return self.update_task(task_id, {"status": status}, custom_task_ids, team_id)
