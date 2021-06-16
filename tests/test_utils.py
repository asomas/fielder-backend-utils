from unittest import TestCase
from google.cloud.firestore import GeoPoint
from fielder_backend_utils import (
    get_with_default,
    make_chunks,
)


class TestUtils(TestCase):
    def test_make_chunks(self):
        n = 10
        c = 3
        l = list(range(n))
        i = 0
        for chunk in make_chunks(l, c):
            start = i * c
            end = min((i + 1) * c, n)
            self.assertEqual(chunk, list(range(start, end)))
            i = i + 1

    def test_get_with_default(self):
        test_data = {"one": "1", "two": None}

        self.assertEqual(get_with_default(test_data, "one", "1"), "1")
        self.assertEqual(get_with_default(test_data, "two", "2"), "2")
        self.assertEqual(get_with_default(test_data, "three", "3"), "3")
