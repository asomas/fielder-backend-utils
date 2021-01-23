from unittest import TestCase
from fielder_backend_utils import (
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
