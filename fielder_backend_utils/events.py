import json
import logging
import os
from enum import Enum, auto
from typing import Union

import google.auth
import google.auth.credentials
from django.utils import timezone
from google.cloud import pubsub_v1
from google.cloud.firestore_v1.document import DocumentReference
from rest_framework import serializers
from rest_framework.request import Request

from fielder_backend_utils.rest_utils import CustomJSONEncoder

logger = logging.getLogger(__name__)


class FielderEventURIScheme(Enum):
    firestore = auto()
    http = auto()
    https = auto()


FIELDER_EVENT_PUBSUB_TOPIC_NAME = "fielder-event"
URI_REGEX = rf"({'|'.join(FielderEventURIScheme._member_names_)})://([\w_-]+(?:(?:[\w_-]+)+))([\w.,@?^=%&:/~+#-]*[\w@?^=%&/~+#-])?"


class FielderEvent(Enum):
    interview_scheduled = auto()
    interview_cancelled = auto()
    upcoming_interview = auto()
    invitation_status_changed = auto()
    offer_status_changed = auto()
    completed_shift_awaiting_approval = auto()
    late_shift_clockin = auto()
    unread_message_notification = auto()


class EventSerialzier(serializers.Serializer):
    source = serializers.RegexField(regex=URI_REGEX)
    resource = serializers.RegexField(regex=URI_REGEX, required=False)
    data = serializers.DictField()
    timestamp = serializers.DateTimeField(default=timezone.now)
    event_id = serializers.ChoiceField(choices=FielderEvent._member_names_)


def publish_event(topic: str, data: dict):
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

    try:
        topic_path = publisher.topic_path(project, topic)
        data = json.dumps(data, cls=CustomJSONEncoder).encode("utf-8")
        future = publisher.publish(topic_path, data)
        logger.info(future.result())
    except Exception as e:
        logger.exception(e)


def publish_fielder_event(
    *,
    source: Union[str, DocumentReference, Request],
    resource: Union[str, DocumentReference],
    organisation_ref: DocumentReference,
    group_ref: DocumentReference,
    data: dict,
    event_id: FielderEvent,
):
    assert organisation_ref and group_ref, "organisation_ref and group_ref are required"

    if isinstance(source, Request):
        if source.firebase_user:
            user_id = source.firebase_user.uid
            if source.data.get("organisation_id"):
                source = f"{FielderEventURIScheme.firestore.name}://organisation_users/{user_id}"
            else:
                source = f"{FielderEventURIScheme.firestore.name}://workers/{user_id}"
        else:
            source = source.build_absolute_uri()
    elif isinstance(source, DocumentReference):
        source = f"{FielderEventURIScheme.firestore.name}://{source.path}"

    if isinstance(resource, DocumentReference):
        resource = f"{FielderEventURIScheme.firestore.name}://{resource.path}"

    logger.info(
        f"Sending {FIELDER_EVENT_PUBSUB_TOPIC_NAME} {event_id.name}, source: {source}, resource: {resource}"
    )

    data["organisation_ref"] = organisation_ref
    data["group_ref"] = group_ref
    ser = EventSerialzier(
        data={
            "source": source,
            "resource": resource,
            "data": data,
            "event_id": event_id.name,
        }
    )
    if not ser.is_valid():
        logger.exception(
            f"Sending {FIELDER_EVENT_PUBSUB_TOPIC_NAME} {event_id.name} failed! source: {source}, resource: {resource}, data: {str(data)}"
        )
    else:
        publish_event(FIELDER_EVENT_PUBSUB_TOPIC_NAME, ser.validated_data)
