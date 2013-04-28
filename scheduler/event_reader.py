"""
Module for reading a list of events from a directory.
"""
from datetime import timedelta, datetime
from event_parser import create_events
from os import walk, stat
from os.path import splitext, join

def _read_files(directory):
    """
    Recursively lists name, first line of content and creation date for all
    files in a folder.
    """
    for path, _, filenames in walk(directory):
        for name, extension in map(splitext, filenames):
            filename = join(path, name + extension)
            contents = open(filename).readline().rstrip()

            creation_stamp = stat(filename).st_mtime
            creation_date = datetime.fromtimestamp(creation_stamp)

            yield name, contents, creation_date

def read_events(directory, max_date=None):
    """
    Extracts events from a files in directory (recursively listed).
    The filename (minus extension) is the event description.
    The file contents are parsed as either an appointment date ('next Friday
    from 4 pm to 8 pm'), or a task with duration and deadline ('4 hours by next
    Friday'). Recurring appointments are also available based on weekdays
    ('every weekday and Saturday from 8 pm to 10 pm').

    max_date is used to limit the number of events created by recurring events.
    
    Returns a list of events that may be missing start date (in case of tasks).
    """
    max_date = max_date or datetime.now() + timedelta(60)
    for name, contents, creation_date in _read_files(directory):
        for event in create_events(name, contents, creation_date, max_date):
            if event.end_date >= datetime.now():
                yield event
            elif not event.start_date:
                raise Exception('Deadline for {} missed!'.format(event.name))
