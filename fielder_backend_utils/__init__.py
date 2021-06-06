import math
from typing import List, Iterator, Dict, Any
from datetime import datetime, timedelta

__version__ = "1.0.11"

WEEKDAYS = [
    "monday",
    "tuesday",
    "wednesday",
    "thursday",
    "friday",
    "saturday",
    "sunday",
]


def hello_fielder():
    print("Hello Fielder")


def make_chunks(item_list: List, chunk_size: int) -> Iterator:
    """
    This function returns a generator
    that yields chunks with size chunk_size,
    with the possibility of the last chunk being smaller
    if the len(item_list) does not divide by chunk_size.

    Args:
        item_list (List): list of objects to chunk
        chunk_size (int): chunk size
    Returns:
        chunk of items_list with size <= chunk_size
    """
    start = 0
    end = min(chunk_size, len(item_list))
    while start < len(item_list):
        yield item_list[start:end]
        start = end
        end = start + chunk_size
        end = min(end, len(item_list))


def next_weekday(d: datetime, weekday: int):
    """
    Get next weekday for given d datetime
    If d is weekday, return d (not d+7)

    Args:
        d (datetime): reference date
        weekday (int): 0=Monday, 1=Tuesday, 2=Wednesday...
        interval (int): week interval
    Returns
        next_weekday (datetime): next weekday from d with given week_interval
    """
    days_ahead = weekday - d.weekday()
    if days_ahead <= 0:
        # Target day already happened this week
        days_ahead += 7
    return d + timedelta(days_ahead)


def prev_weekday(d: datetime, weekday: int):
    """
    Get prev weekday for given d datetime
    If d is weekday, return d (not d-7)

    Args:
        d (datetime): reference date
        weekday (int): 0=Monday, 1=Tuesday, 2=Wednesday...
        interval (int): week interval
    Returns
        prev_weekday (datetime): previous weekday until d with given week_interval
    """
    days_behind = d.weekday() - weekday
    if days_behind < 0:
        # Target day has not happened this week
        days_behind += 7
    return d - timedelta(days_behind)


def matches_recurrence(
    scheduled_date: datetime, recurrence: dict, start_date: datetime
) -> bool:
    """
    Return True if a scheduled_date matches a recurrence rule that starts from start_date
    Currently only support weekly recurrence type

    Args:
        scheduled_date (datetime): scheduled date
        recurrence (dict): recurrence rule
        start_date (datetime): recurrence start date
    Returns:
        match (bool)
    """
    if recurrence["repeat_interval_type"] is None:
        return start_date.date() == scheduled_date.date()

    interval_type = recurrence["repeat_interval_type"].lower()
    assert interval_type in [
        "daily",
        "weekly",
    ], "only weekly, daily and None type supported"

    interval_amount = recurrence["interval_amount"]
    assert interval_amount > 0, "interval amount must be > 0"

    if interval_type == "daily":
        delta_days = (scheduled_date - start_date).days
        return delta_days % interval_amount == 0

    elif interval_type == "weekly":
        if not recurrence[WEEKDAYS[scheduled_date.weekday()]]:
            return False
        else:
            first_scheduled_date = next_weekday(start_date, scheduled_date.weekday())
            # week_delta = math.ceil((scheduled_date - first_scheduled_date).days / 7)
            week_delta = round((scheduled_date - first_scheduled_date).days / 7)
            return week_delta % interval_amount == 0


def matches_shift(dt: datetime, shift_data: Dict[str, Any]) -> bool:
    """
    Return True if a given datetime dt is within job_shifts start_date-end_date,
    and matches the weekday matches the recurrence

    Args:
        dt (datetime): scheduled date
        shift_data (dict): job_shifts data
    Returns:
        match (bool)
    """
    match = False
    if shift_data["start_date"] <= dt <= shift_data["end_date"]:
        match = matches_recurrence(
            dt, shift_data["recurrence"], shift_data["start_date"]
        )
    return match


def count_shift_days(shift_data: Dict[str, Any]) -> int:
    """
    Return number of valid days in shift_data
    :param shift_data: shift data
    :return: total_days
    """
    start_date = shift_data["start_date"]
    end_date = shift_data["end_date"]
    recurrence = shift_data["recurrence"]
    if recurrence["repeat_interval_type"] is None:
        return 1  # only on start_date

    interval_type = recurrence["repeat_interval_type"].lower()
    assert interval_type in [
        "daily",
        "weekly",
    ], "only weekly, daily and None type supported"

    interval_amount = recurrence["interval_amount"]
    assert interval_amount > 0, "interval amount must be > 0"

    if interval_type == "daily":
        delta_days = (end_date - start_date).days
        return delta_days // interval_amount + 1

    elif interval_type == "weekly":
        total_days = 0
        for i, day_name in enumerate(WEEKDAYS):
            if recurrence[day_name]:
                first_scheduled_date = next_weekday(start_date, i)
                last_scheduled_date = prev_weekday(end_date, i)
                week_delta = (last_scheduled_date - first_scheduled_date).days // 7
                if interval_amount == 1:
                    total_days += week_delta + 1
                else:
                    total_days += week_delta // interval_amount + 1
        return total_days


if __name__ == "__main__":
    pass
