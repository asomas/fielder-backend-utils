import json
import logging
from datetime import datetime
from typing import Dict

import google.auth
from django.conf import settings
from google.cloud import tasks
from google.protobuf import timestamp_pb2

logger = logging.getLogger(__name__)


def create_http_task(
    http_url: str,
    queue: str,
    queue_location: str,
    payload: Dict = None,
    http_method: str = "POST",
    scheduled_at: datetime = None,
):
    """
    Create a cloud task job that triggers HTTP url
    """

    # get default credentials
    # for some unknown reason, in app engine standard
    # credentials.service_account_email == 'default'
    # so we don't have choice but to set correct email in
    # secret manager variable
    credentials, project = google.auth.default()
    service_account_email = credentials.service_account_email
    if service_account_email == "default":
        service_account_email = settings.SERVICE_ACCOUNT_EMAIL

    # oidc_token is required to authenticate
    # cloud run async invocation
    # reference https://cloud.google.com/run/docs/triggering/using-tasks
    task = {
        "http_request": {
            "http_method": http_method,
            "url": http_url,
            "headers": {
                "Content-Type": "application/json",
            },
            "oidc_token": {
                "service_account_email": service_account_email,
            },
        }
    }

    if payload is not None:
        task["http_request"]["body"] = json.dumps(payload).encode()

    if scheduled_at is not None:
        schedule_time = timestamp_pb2.Timestamp()
        schedule_time.FromDatetime(scheduled_at)
        task["schedule_time"] = schedule_time

    client = tasks.CloudTasksClient()
    parent = client.queue_path(project, queue_location, queue)
    req = {"parent": parent, "task": task}
    try:
        response = client.create_task(request=req)
    except Exception as e:
        logger.error(str(req))
        raise e
    return response
