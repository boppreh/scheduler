"""
Module for reading and arranging a schedule based on a user-created directory.
"""

from .scheduler import schedule
from .event_reader import read_events

def get_full_schedule(directory='../events/', max_date=None):
    """ Returns the scheduled events from a given directory. """
    raw_events = read_events(directory, max_date)
    events = schedule(raw_events)
    events.sort(key=lambda e: e.start_date)
    return events

if __name__ == '__main__':
    print('\n'.join(map(str, get_full_schedule())))
