import math
from typing import List, Iterator
from datetime import datetime, timedelta

WEEKDAYS = ['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday']

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
    if days_ahead < 0: 
        # Target day already happened this week
        days_ahead += 7
    return d + timedelta(days_ahead)

def matches_reccurence(scheduled_date: datetime, recurrence: dict, start_date: datetime) -> bool:
    """
    Return True if a scheduled_date matches a reccurence rule that starts from start_date
    Currently only support weekly recurrence type

    Args:
        scheduled_date (datetime): scheduled date
        recurrence (dict): recurrence rule
        start_date (datetime): recurrence start date
    Returns:
        match (bool)
    """    
    assert recurrence['repeat_interval_type'].lower() == 'weekly', 'only weekly type supported'
    if not recurrence[WEEKDAYS[scheduled_date.weekday()]]:
        return False
    else:
        first_scheduled_date = next_weekday(start_date, scheduled_date.weekday())
        week_delta = math.ceil((scheduled_date - first_scheduled_date).days / 7)
        return week_delta % recurrence['interval_amount'] == 0

if __name__ == '__main__':
    pass
