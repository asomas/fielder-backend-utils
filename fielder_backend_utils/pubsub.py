import json
import logging
import os

import google.auth
import google.auth.credentials
from google.cloud import pubsub_v1

from fielder_backend_utils.rest_utils import CustomJSONEncoder

logger = logging.getLogger(__name__)

# init client
if os.getenv("PUBSUB_EMULATOR_HOST") and os.getenv("PUBSUB_PROJECT_ID"):
    from unittest import mock

    cred = mock.Mock(spec=google.auth.credentials.Credentials)
    project = os.getenv("PUBSUB_PROJECT_ID")
    publisher = pubsub_v1.PublisherClient(credentials=cred)
    subscriber = pubsub_v1.SubscriberClient(credentials=cred)
else:
    cred, project = google.auth.default()
    publisher = pubsub_v1.PublisherClient()
    subscriber = pubsub_v1.SubscriberClient()


def publish_event(topic: str, data: dict):
    try:
        topic_path = publisher.topic_path(project, topic)
        data = json.dumps(data, cls=CustomJSONEncoder).encode("utf-8")
        future = publisher.publish(topic_path, data)
        logger.info(future.result())
    except Exception as e:
        logger.error(f"Failed to publish {topic}")
        logger.exception(e)
