import random
import string
from hashlib import sha256
from urllib.parse import quote_plus

import requests

from fielder_backend_utils.intercom import IntercomClient


def create_clickup_task(task_title, list_id, token, task_description="n/a"):
    response = requests.post(
        f"https://api.clickup.com/api/v2/list/{list_id}/task/",
        json={
            "name": task_title,
            "description": task_description,
        },
        headers={"Authorization": token},
    )


ALPHABET = string.digits + string.ascii_uppercase


def baseNEncode(number, *, base=36):
    """Converts an integer to a base36 string."""
    letters = ALPHABET[0:base]
    if not isinstance(number, int):
        raise TypeError("number must be an integer")

    base36 = ""

    if number < 0:
        raise ValueError("number cannot be less than 0")

    if 0 <= number < base:
        return letters[number]

    while number != 0:
        number, i = divmod(number, len(letters))
        base36 = letters[i] + base36

    return base36


def baseNDecode(number, *, base=36):
    return int(number, base)


def make_id(str_val, length, attempts_before_fallback=None):
    """
    A generator that Yields IDs deterministically from the input, that are likely to be unique assuming that the input is unique.
    * The first 10 IDs are produced using SHA256 hashing (see below).
    * After 10 yields, the generator resorts to a pseudo random generator.
    * The generated IDs are strings (with given length) of uppercase letters and numbers.
    Implementation:
    * This function works by hashing (using SHA256) the input string and outputing a base 36 encoding of the first N bytes where N is sufficiently large to map to m letters, m is ID length.
    * If another value is required, the hash (all 256 bits) is then rehashed and again a base 36 encoding of the first n bytes yielded.
    * After 10 attempts, a pseudo random generator is used, seeded with the input string.
    """
    attempts_before_fallback = attempts_before_fallback or length * 3
    input_bytes = bytearray(str_val, "utf-8")
    random.seed(str_val)
    try_count = 0
    while True:
        if try_count < attempts_before_fallback:
            try_count += 1
        else:
            yield "".join(random.choice(ALPHABET) for i in range(length))
        h = sha256()
        h.update(input_bytes)
        hash_bytes = h.digest()
        hash_bytes_as_int = int.from_bytes(hash_bytes, "big", signed=False)
        result = baseNEncode(hash_bytes_as_int, base=36)
        yield result[:length]
        input_bytes = h.digest()


def get_retool_environment(server_mode: str) -> str:
    env = ""
    if server_mode.lower() == "prod":
        env = "production"
    elif server_mode.lower() == "dev":
        env = "staging"
    return env


def get_worker_retool_link(
    retool_app_id: str,
    phone: str,
    server_mode: str,
    tab: int = 0,
) -> str:
    return f"https://asomas.retool.com/apps/{retool_app_id}?phone={quote_plus(phone)}&_environment={get_retool_environment(server_mode)}&tab={str(tab)}"


def get_worker_intercom_link(
    intercom_access_token: str,
    intercom_app_id: str,
    worker_id: str,
) -> str:
    return f"https://app.intercom.com/a/apps/{intercom_app_id}/users/{IntercomClient(intercom_access_token).get_user(worker_id)['id']}"
