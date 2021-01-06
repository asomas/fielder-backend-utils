from unittest import TestCase
from datetime import datetime
from fielder_backend_utils import (
    WEEKDAYS,
    make_chunks,
    next_weekday,
    matches_reccurence,
)

class TestUtils(TestCase):
    def test_make_chunks(self):
        n = 10
        c = 3
        l = list(range(n))
        i = 0
        for chunk in make_chunks(l, c):
            start = i*c
            end = min((i+1)*c, n)
            self.assertEqual(chunk, list(range(start, end)))
            i = i+1

    def test_next_weekday(self):
        self.assertEqual(next_weekday(datetime(2021,1,1), WEEKDAYS.index('saturday')), datetime(2021,1,2))
        self.assertEqual(next_weekday(datetime(2021,1,1), WEEKDAYS.index('monday')), datetime(2021,1,4))
        self.assertEqual(next_weekday(datetime(2021,1,1), WEEKDAYS.index('friday')), datetime(2021,1,1))

    def test_matches_reccurence(self):
        # negative: reject other repeat_interval_type other than Weekly
        start_date = datetime(2021,1,1)
        scheduled_date = datetime(2021,1,6)
        reccurence = {
            'repeat_interval_type': 'Monthly',
            'interval_amount': 1,
            'monday': True, 'tuesday': False, 'wednesday': False, 'thursday': False, 'friday': False, 'saturday': False, 'sunday': False,
        }
        self.assertRaises(AssertionError, matches_reccurence, scheduled_date, reccurence, start_date)

        # positive
        start_date = datetime(2021,1,1)
        scheduled_date = datetime(2021,1,4)
        reccurence = {
            'repeat_interval_type': 'Weekly',
            'interval_amount': 1,
            'monday': True, 'tuesday': False, 'wednesday': False, 'thursday': False, 'friday': False, 'saturday': False, 'sunday': False,
        }
        self.assertTrue(matches_reccurence(scheduled_date, reccurence, start_date))

        # negative: different day
        start_date = datetime(2021,1,1)
        scheduled_date = datetime(2021,1,5)
        reccurence = {
            'repeat_interval_type': 'Weekly',
            'interval_amount': 1,
            'monday': True, 'tuesday': False, 'wednesday': False, 'thursday': False, 'friday': False, 'saturday': False, 'sunday': False,
        }
        self.assertFalse(matches_reccurence(scheduled_date, reccurence, start_date))        

        # positive: biweekly
        start_date = datetime(2021,1,1)
        scheduled_date = datetime(2021,1,18)
        reccurence = {
            'repeat_interval_type': 'Weekly',
            'interval_amount': 2,
            'monday': True, 'tuesday': False, 'wednesday': False, 'thursday': False, 'friday': False, 'saturday': False, 'sunday': False,
        }
        self.assertTrue(matches_reccurence(scheduled_date, reccurence, start_date))

        # negative: biweekly, wrong week
        start_date = datetime(2021,1,1)
        scheduled_date = datetime(2021,1,11)
        reccurence = {
            'repeat_interval_type': 'Weekly',
            'interval_amount': 2,
            'monday': True, 'tuesday': False, 'wednesday': False, 'thursday': False, 'friday': False, 'saturday': False, 'sunday': False,
        }
        self.assertFalse(matches_reccurence(scheduled_date, reccurence, start_date))
