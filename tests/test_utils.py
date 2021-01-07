from unittest import TestCase
from datetime import datetime
from fielder_backend_utils import (
    WEEKDAYS,
    make_chunks,
    next_weekday,
    matches_recurrence,
    matches_shift,
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

    def test_matches_recurrence(self):
        # negative: reject other repeat_interval_type other than Weekly
        start_date = datetime(2021,1,1)
        scheduled_date = datetime(2021,1,6)
        recurrence = {
            'repeat_interval_type': 'Monthly',
            'interval_amount': 1,
            'monday': True, 'tuesday': False, 'wednesday': False, 'thursday': False, 'friday': False, 'saturday': False, 'sunday': False,
        }
        self.assertRaises(AssertionError, matches_recurrence, scheduled_date, recurrence, start_date)

        # positive None
        start_date = datetime(2021,1,1)
        scheduled_date = datetime(2021,1,1)
        recurrence = {
            'repeat_interval_type': None,
            'interval_amount': 0,
            'monday': False, 'tuesday': False, 'wednesday': False, 'thursday': False, 'friday': False, 'saturday': False, 'sunday': False,
        }
        self.assertTrue(matches_recurrence(scheduled_date, recurrence, start_date))

        # positive None (with hour)
        start_date = datetime(2021,1,1,7)
        scheduled_date = datetime(2021,1,1,8)
        recurrence = {
            'repeat_interval_type': None,
            'interval_amount': 0,
            'monday': False, 'tuesday': False, 'wednesday': False, 'thursday': False, 'friday': False, 'saturday': False, 'sunday': False,
        }
        self.assertTrue(matches_recurrence(scheduled_date, recurrence, start_date))

        # negative None
        start_date = datetime(2021,1,1)
        scheduled_date = datetime(2021,1,8)
        recurrence = {
            'repeat_interval_type': None,
            'interval_amount': 0,
            'monday': False, 'tuesday': False, 'wednesday': False, 'thursday': False, 'friday': False, 'saturday': False, 'sunday': False,
        }
        self.assertFalse(matches_recurrence(scheduled_date, recurrence, start_date))

        # positive daily
        start_date = datetime(2021,1,1)
        scheduled_date = datetime(2021,1,3)
        recurrence = {
            'repeat_interval_type': 'Daily',
            'interval_amount': 1,
            'monday': False, 'tuesday': False, 'wednesday': False, 'thursday': False, 'friday': False, 'saturday': False, 'sunday': False,
        }
        self.assertTrue(matches_recurrence(scheduled_date, recurrence, start_date))

        # positive weekly
        start_date = datetime(2021,1,1)
        scheduled_date = datetime(2021,1,4)
        recurrence = {
            'repeat_interval_type': 'Weekly',
            'interval_amount': 1,
            'monday': True, 'tuesday': False, 'wednesday': False, 'thursday': False, 'friday': False, 'saturday': False, 'sunday': False,
        }
        self.assertTrue(matches_recurrence(scheduled_date, recurrence, start_date))

        # negative: different day
        start_date = datetime(2021,1,1)
        scheduled_date = datetime(2021,1,5)
        recurrence = {
            'repeat_interval_type': 'Weekly',
            'interval_amount': 1,
            'monday': True, 'tuesday': False, 'wednesday': False, 'thursday': False, 'friday': False, 'saturday': False, 'sunday': False,
        }
        self.assertFalse(matches_recurrence(scheduled_date, recurrence, start_date))        

        # positive: biweekly
        start_date = datetime(2021,1,1)
        scheduled_date = datetime(2021,1,18)
        recurrence = {
            'repeat_interval_type': 'Weekly',
            'interval_amount': 2,
            'monday': True, 'tuesday': False, 'wednesday': False, 'thursday': False, 'friday': False, 'saturday': False, 'sunday': False,
        }
        self.assertTrue(matches_recurrence(scheduled_date, recurrence, start_date))

        # negative: biweekly, wrong week
        start_date = datetime(2021,1,1)
        scheduled_date = datetime(2021,1,11)
        recurrence = {
            'repeat_interval_type': 'Weekly',
            'interval_amount': 2,
            'monday': True, 'tuesday': False, 'wednesday': False, 'thursday': False, 'friday': False, 'saturday': False, 'sunday': False,
        }
        self.assertFalse(matches_recurrence(scheduled_date, recurrence, start_date))

        # positive: triweekly
        start_date = datetime(2021,1,1)
        scheduled_date = datetime(2021,1,25)
        recurrence = {
            'repeat_interval_type': 'Weekly',
            'interval_amount': 3,
            'monday': True, 'tuesday': False, 'wednesday': False, 'thursday': False, 'friday': False, 'saturday': False, 'sunday': False,
        }
        self.assertTrue(matches_recurrence(scheduled_date, recurrence, start_date))

        # negative: triweekly, wrong week
        start_date = datetime(2021,1,1)
        scheduled_date = datetime(2021,1,18)
        recurrence = {
            'repeat_interval_type': 'Weekly',
            'interval_amount': 3,
            'monday': True, 'tuesday': False, 'wednesday': False, 'thursday': False, 'friday': False, 'saturday': False, 'sunday': False,
        }
        self.assertFalse(matches_recurrence(scheduled_date, recurrence, start_date))

    def test_matches_shift(self):
        # positive None        
        scheduled_date = datetime(2021,1,1)
        shift_data = {
            'start_date': datetime(2021,1,1),
            'end_date': datetime(2022,1,1),
            'recurrence': {
                'repeat_interval_type': None,
                'interval_amount': 0,
                'monday': False, 'tuesday': False, 'wednesday': False, 'thursday': False, 'friday': False, 'saturday': False, 'sunday': False,
            }
        }
        self.assertTrue(matches_shift(scheduled_date, shift_data))

        # positive weekly
        scheduled_date = datetime(2021,1,4)
        shift_data = {
            'start_date': datetime(2021,1,1),
            'end_date': datetime(2022,1,1),
            'recurrence': {
                'repeat_interval_type': 'Weekly',
                'interval_amount': 1,
                'monday': True, 'tuesday': False, 'wednesday': False, 'thursday': False, 'friday': False, 'saturday': False, 'sunday': False,
            }
        }
        self.assertTrue(matches_shift(scheduled_date, shift_data))