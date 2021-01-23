from unittest import TestCase
from datetime import datetime
from fielder_backend_utils import (
    WEEKDAYS,
    next_weekday,
    prev_weekday,
    matches_recurrence,
    matches_shift,
    count_shift_days,
)


class TestShift(TestCase):
    def test_next_weekday(self):
        self.assertEqual(
            next_weekday(datetime(2021, 1, 1), WEEKDAYS.index("saturday")),
            datetime(2021, 1, 2),
        )
        self.assertEqual(
            next_weekday(datetime(2021, 1, 1), WEEKDAYS.index("monday")),
            datetime(2021, 1, 4),
        )
        self.assertEqual(
            next_weekday(datetime(2021, 1, 1), WEEKDAYS.index("friday")),
            datetime(2021, 1, 1),
        )

    def test_prev_weekday(self):
        self.assertEqual(
            prev_weekday(datetime(2021, 1, 6), WEEKDAYS.index("wednesday")),
            datetime(2021, 1, 6),
        )
        self.assertEqual(
            prev_weekday(datetime(2021, 1, 6), WEEKDAYS.index("tuesday")),
            datetime(2021, 1, 5),
        )
        self.assertEqual(
            prev_weekday(datetime(2021, 1, 6), WEEKDAYS.index("monday")),
            datetime(2021, 1, 4),
        )
        self.assertEqual(
            prev_weekday(datetime(2021, 1, 6), WEEKDAYS.index("friday")),
            datetime(2021, 1, 1),
        )
        self.assertEqual(
            prev_weekday(datetime(2021, 1, 6), WEEKDAYS.index("thursday")),
            datetime(2020, 12, 31),
        )

    def test_matches_recurrence(self):
        # negative: reject other repeat_interval_type other than Weekly
        start_date = datetime(2021, 1, 1)
        scheduled_date = datetime(2021, 1, 6)
        recurrence = {
            "repeat_interval_type": "Monthly",
            "interval_amount": 1,
            "monday": True,
            "tuesday": False,
            "wednesday": False,
            "thursday": False,
            "friday": False,
            "saturday": False,
            "sunday": False,
        }
        self.assertRaises(
            AssertionError, matches_recurrence, scheduled_date, recurrence, start_date
        )

        # positive None
        start_date = datetime(2021, 1, 1)
        scheduled_date = datetime(2021, 1, 1)
        recurrence = {
            "repeat_interval_type": None,
            "interval_amount": 0,
            "monday": False,
            "tuesday": False,
            "wednesday": False,
            "thursday": False,
            "friday": False,
            "saturday": False,
            "sunday": False,
        }
        self.assertTrue(matches_recurrence(scheduled_date, recurrence, start_date))

        # positive None (with hour)
        start_date = datetime(2021, 1, 1, 7)
        scheduled_date = datetime(2021, 1, 1, 8)
        recurrence = {
            "repeat_interval_type": None,
            "interval_amount": 0,
            "monday": False,
            "tuesday": False,
            "wednesday": False,
            "thursday": False,
            "friday": False,
            "saturday": False,
            "sunday": False,
        }
        self.assertTrue(matches_recurrence(scheduled_date, recurrence, start_date))

        # negative None
        start_date = datetime(2021, 1, 1)
        scheduled_date = datetime(2021, 1, 8)
        recurrence = {
            "repeat_interval_type": None,
            "interval_amount": 0,
            "monday": False,
            "tuesday": False,
            "wednesday": False,
            "thursday": False,
            "friday": False,
            "saturday": False,
            "sunday": False,
        }
        self.assertFalse(matches_recurrence(scheduled_date, recurrence, start_date))

        # positive daily
        start_date = datetime(2021, 1, 1)
        scheduled_date = datetime(2021, 1, 3)
        recurrence = {
            "repeat_interval_type": "Daily",
            "interval_amount": 1,
            "monday": False,
            "tuesday": False,
            "wednesday": False,
            "thursday": False,
            "friday": False,
            "saturday": False,
            "sunday": False,
        }
        self.assertTrue(matches_recurrence(scheduled_date, recurrence, start_date))

        # positive weekly
        start_date = datetime(2021, 1, 1)
        scheduled_date = datetime(2021, 1, 4)
        recurrence = {
            "repeat_interval_type": "Weekly",
            "interval_amount": 1,
            "monday": True,
            "tuesday": False,
            "wednesday": False,
            "thursday": False,
            "friday": False,
            "saturday": False,
            "sunday": False,
        }
        self.assertTrue(matches_recurrence(scheduled_date, recurrence, start_date))

        # negative: different day
        start_date = datetime(2021, 1, 1)
        scheduled_date = datetime(2021, 1, 5)
        recurrence = {
            "repeat_interval_type": "Weekly",
            "interval_amount": 1,
            "monday": True,
            "tuesday": False,
            "wednesday": False,
            "thursday": False,
            "friday": False,
            "saturday": False,
            "sunday": False,
        }
        self.assertFalse(matches_recurrence(scheduled_date, recurrence, start_date))

        # positive: biweekly
        start_date = datetime(2021, 1, 1)
        scheduled_date = datetime(2021, 1, 18)
        recurrence = {
            "repeat_interval_type": "Weekly",
            "interval_amount": 2,
            "monday": True,
            "tuesday": False,
            "wednesday": False,
            "thursday": False,
            "friday": False,
            "saturday": False,
            "sunday": False,
        }
        self.assertTrue(matches_recurrence(scheduled_date, recurrence, start_date))

        # negative: biweekly, wrong week
        start_date = datetime(2021, 1, 1)
        scheduled_date = datetime(2021, 1, 11)
        recurrence = {
            "repeat_interval_type": "Weekly",
            "interval_amount": 2,
            "monday": True,
            "tuesday": False,
            "wednesday": False,
            "thursday": False,
            "friday": False,
            "saturday": False,
            "sunday": False,
        }
        self.assertFalse(matches_recurrence(scheduled_date, recurrence, start_date))

        # positive: triweekly
        start_date = datetime(2021, 1, 1)
        scheduled_date = datetime(2021, 1, 25)
        recurrence = {
            "repeat_interval_type": "Weekly",
            "interval_amount": 3,
            "monday": True,
            "tuesday": False,
            "wednesday": False,
            "thursday": False,
            "friday": False,
            "saturday": False,
            "sunday": False,
        }
        self.assertTrue(matches_recurrence(scheduled_date, recurrence, start_date))

        # negative: triweekly, wrong week
        start_date = datetime(2021, 1, 1)
        scheduled_date = datetime(2021, 1, 18)
        recurrence = {
            "repeat_interval_type": "Weekly",
            "interval_amount": 3,
            "monday": True,
            "tuesday": False,
            "wednesday": False,
            "thursday": False,
            "friday": False,
            "saturday": False,
            "sunday": False,
        }
        self.assertFalse(matches_recurrence(scheduled_date, recurrence, start_date))

    def test_matches_shift(self):
        # positive None
        scheduled_date = datetime(2021, 1, 1)
        shift_data = {
            "start_date": datetime(2021, 1, 1),
            "end_date": datetime(2022, 1, 1),
            "recurrence": {
                "repeat_interval_type": None,
                "interval_amount": 0,
                "monday": False,
                "tuesday": False,
                "wednesday": False,
                "thursday": False,
                "friday": False,
                "saturday": False,
                "sunday": False,
            },
        }
        self.assertTrue(matches_shift(scheduled_date, shift_data))

        # positive weekly
        scheduled_date = datetime(2021, 1, 4)
        shift_data = {
            "start_date": datetime(2021, 1, 1),
            "end_date": datetime(2022, 1, 1),
            "recurrence": {
                "repeat_interval_type": "Weekly",
                "interval_amount": 1,
                "monday": True,
                "tuesday": False,
                "wednesday": False,
                "thursday": False,
                "friday": False,
                "saturday": False,
                "sunday": False,
            },
        }
        self.assertTrue(matches_shift(scheduled_date, shift_data))

    def test_count_shift_days_non_recurring_and_daily(self):
        # non-recurring
        shift_data = {
            "start_date": datetime(2021, 1, 1),
            "end_date": datetime(2021, 1, 1),
            "recurrence": {
                "repeat_interval_type": None,
                "interval_amount": 0,
                "monday": False,
                "tuesday": False,
                "wednesday": False,
                "thursday": False,
                "friday": False,
                "saturday": False,
                "sunday": False,
            },
        }
        self.assertEqual(count_shift_days(shift_data), 1)

        # daily
        shift_data = {
            "start_date": datetime(2021, 1, 1),
            "end_date": datetime(2021, 1, 8),
            "recurrence": {
                "repeat_interval_type": "Daily",
                "interval_amount": 1,
                "monday": False,
                "tuesday": False,
                "wednesday": False,
                "thursday": False,
                "friday": False,
                "saturday": False,
                "sunday": False,
            },
        }
        self.assertEqual(count_shift_days(shift_data), 7)

        # daily every 2 days
        shift_data = {
            "start_date": datetime(2021, 1, 1),
            "end_date": datetime(2021, 1, 8),
            "recurrence": {
                "repeat_interval_type": "Daily",
                "interval_amount": 2,
                "monday": False,
                "tuesday": False,
                "wednesday": False,
                "thursday": False,
                "friday": False,
                "saturday": False,
                "sunday": False,
            },
        }
        self.assertEqual(count_shift_days(shift_data), 4)

        # daily every 3 days
        shift_data = {
            "start_date": datetime(2021, 1, 1),
            "end_date": datetime(2021, 1, 8),
            "recurrence": {
                "repeat_interval_type": "Daily",
                "interval_amount": 3,
                "monday": False,
                "tuesday": False,
                "wednesday": False,
                "thursday": False,
                "friday": False,
                "saturday": False,
                "sunday": False,
            },
        }
        self.assertEqual(count_shift_days(shift_data), 3)

        shift_data = {
            "start_date": datetime(2021, 1, 1),
            "end_date": datetime(2021, 1, 15),
            "recurrence": {
                "repeat_interval_type": "Daily",
                "interval_amount": 3,
                "monday": False,
                "tuesday": False,
                "wednesday": False,
                "thursday": False,
                "friday": False,
                "saturday": False,
                "sunday": False,
            },
        }
        self.assertEqual(count_shift_days(shift_data), 5)

        # daily every 7 days
        shift_data = {
            "start_date": datetime(2021, 1, 1),
            "end_date": datetime(2021, 1, 8),
            "recurrence": {
                "repeat_interval_type": "Daily",
                "interval_amount": 7,
                "monday": False,
                "tuesday": False,
                "wednesday": False,
                "thursday": False,
                "friday": False,
                "saturday": False,
                "sunday": False,
            },
        }
        self.assertEqual(count_shift_days(shift_data), 2)

        # daily every 8 days
        shift_data = {
            "start_date": datetime(2021, 1, 1),
            "end_date": datetime(2021, 1, 9),
            "recurrence": {
                "repeat_interval_type": "Daily",
                "interval_amount": 8,
                "monday": False,
                "tuesday": False,
                "wednesday": False,
                "thursday": False,
                "friday": False,
                "saturday": False,
                "sunday": False,
            },
        }
        self.assertEqual(count_shift_days(shift_data), 2)

        # every 12 days
        shift_data = {
            "start_date": datetime(2021, 1, 1),
            "end_date": datetime(2021, 1, 25),
            "recurrence": {
                "repeat_interval_type": "Daily",
                "interval_amount": 12,
                "monday": False,
                "tuesday": False,
                "wednesday": False,
                "thursday": False,
                "friday": False,
                "saturday": False,
                "sunday": False,
            },
        }
        self.assertEqual(count_shift_days(shift_data), 3)

        # daily every 14 days across month
        shift_data = {
            "start_date": datetime(2021, 1, 1),
            "end_date": datetime(2021, 2, 12),
            "recurrence": {
                "repeat_interval_type": "Daily",
                "interval_amount": 14,
                "monday": False,
                "tuesday": False,
                "wednesday": False,
                "thursday": False,
                "friday": False,
                "saturday": False,
                "sunday": False,
            },
        }
        self.assertEqual(count_shift_days(shift_data), 4)

    def test_count_shift_days_non_weekly(self):
        # weekly
        shift_data = {
            "start_date": datetime(2021, 1, 1),
            "end_date": datetime(2021, 1, 8),
            "recurrence": {
                "repeat_interval_type": "Weekly",
                "interval_amount": 1,
                "monday": True,
                "tuesday": True,
                "wednesday": False,
                "thursday": False,
                "friday": False,
                "saturday": False,
                "sunday": False,
            },
        }
        self.assertEqual(count_shift_days(shift_data), 2)

        # weekly II
        shift_data = {
            "start_date": datetime(2021, 1, 1),
            "end_date": datetime(2021, 1, 22),
            "recurrence": {
                "repeat_interval_type": "Weekly",
                "interval_amount": 1,
                "monday": True,
                "tuesday": True,
                "wednesday": True,
                "thursday": False,
                "friday": False,
                "saturday": False,
                "sunday": False,
            },
        }
        self.assertEqual(count_shift_days(shift_data), 9)

        # bi-weekly
        shift_data = {
            "start_date": datetime(2021, 1, 1),
            "end_date": datetime(2021, 1, 29),
            "recurrence": {
                "repeat_interval_type": "Weekly",
                "interval_amount": 2,
                "monday": False,
                "tuesday": False,
                "wednesday": False,
                "thursday": False,
                "friday": True,
                "saturday": False,
                "sunday": False,
            },
        }
        self.assertEqual(count_shift_days(shift_data), 3)

        # bi-weekly II
        shift_data = {
            "start_date": datetime(2021, 1, 1),
            "end_date": datetime(2021, 3, 1),
            "recurrence": {
                "repeat_interval_type": "Weekly",
                "interval_amount": 2,
                "monday": True,
                "tuesday": False,
                "wednesday": False,
                "thursday": True,
                "friday": False,
                "saturday": False,
                "sunday": False,
            },
        }
        self.assertEqual(count_shift_days(shift_data), 9)
