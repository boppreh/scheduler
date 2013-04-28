"""
Module for parsing a list of events from a given description.
"""
from parsedatetime.parsedatetime import Calendar
from datetime import datetime, timedelta

# The parsedatetime library is way too chatty by default.
import logging
logging.getLogger().setLevel(logging.WARNING)
calendar = Calendar()
one_day = timedelta(days=1)

class Event(object):
    # Example:
    # Clean bedroom: 2012-11-02 16:00:00 - 2012-11-02 17:30:00 (1:30:00)
    format_string = '{0[name]}: {0[start_date]} - {0[end_date]} ({0[duration]})'

    """
    Class for storing an event. The event may have a start and end date
    (appointment) or a duration and deadline (task).
    """
    def __init__(self, name, start_date, duration, end_date):
        self.name = name
        self.start_date = start_date
        self.duration = duration
        self.end_date = end_date

    def __str__(self):
        return Event.format_string.format(self.__dict__)

def _parse_duration(duration_str):
    time, unit = duration_str.split()
    time = float(time)
    if 'hour' in unit:
        return timedelta(hours=time)
    elif 'minute' in unit:
        return timedelta(minutes=time)
    elif 'second' in unit:
        return timedelta(seconds=time)

def _parse(strings, source_time):
    """
    Returns the datetime of each natural language string, using the
    previous datetime as base time for the next. source_time defaults to the
    current datetime.
    """
    for string in strings:
        tuple_result, flag = calendar.parse(string, source_time)
        date_result = datetime(*tuple_result[:6])

        # Make sure the strings follow a monotonic sequence.
        if date_result < source_time and string != strings[0]:
            date_result += one_day

        # Remove information about weekday and microseconds.
        yield date_result 
        # Use this date as the base for the next date.
        # The use case for this is: (from) 'next Friday 4 pm' (to) '8 pm'
        # The second value should be in the "next Friday" context, not today.
        source_time = date_result

def _parse_referenced_days(days):
    """
    Converts a list of day names into a boolean list with all week days, with
    True if the day was referenced and False otherwise.

    ['monday', 'saturday'] => [True, False, False, False, False, True, False]
    ['monday', 'weekend'] => [True, False, False, False, False, True, True]
    """
    # Names for the days of the week in the same order they'll be registered in
    # the following map.
    days_of_the_week = ['monday', 'tuesday', 'wednesday', 'thursday', 'friday',
                        'saturday', 'sunday']

    week_map = [False] * 7

    if 'weekday' in days:
        days.remove('weekday')
        days.extend(days_of_the_week[:5])
    if 'weekend' in days:
        days.remove('weekend')
        days.extend(days_of_the_week[6:])
    if 'day' in days:
        days.remove('day')
        days.extend(days_of_the_week)

    for day in days:
        # Maps the string back to an index in the week_map and sets it to true.
        # Ignores repeated values.
        week_map[days_of_the_week.index(day)] = True

    return week_map

def _parse_week_map(days_str):
    """
    Converts a string referencing days of the week into a boolean list with all
    days and their membership status.

    'weekend and Monday' => [True, False, False, False, False, True, True]
    'weekday except Monday' => [False, True, True, True, True, False, False]
    """
    normalized_str = days_str.replace(',', ' ').replace(' and ', ' ').lower()
    if 'except' in normalized_str:
        positive_days, negative_days = normalized_str.split(' except ')
    else:
        positive_days = normalized_str
        negative_days = ''

    positive_week_map = _parse_referenced_days(positive_days.split())
    negative_week_map = _parse_referenced_days(negative_days.split())

    return [p and not n for p, n in zip(positive_week_map, negative_week_map)]

def _create_recurring_events(name, days, period, base_date, max_date):
    """
    Creates a series of events following a recurring pattern.

    name defines the name of all events.
    days is a list of human readable strings defining the days of the week that
        the event will recurr ('Monday', 'weekend', etc).
    period is a human readable string defining the time period of each event
        ('12 am to 4:30 pm')
    base_date is the starting day for the first event
    max_date is the limit date for the generated events.
    """
    week_map = _parse_week_map(days)
    while base_date < max_date:
        # _parse period.
        start_date, end_date = _parse(period.split(' to '), base_date)

        # Ignores if not in a selected day of the week.
        if week_map[start_date.weekday()]:
            yield Event(name, start_date, end_date - start_date, end_date)

        # Try next day.
        base_date += one_day

def create_events(name, contents, creation_date, max_date):
    """
    Creates a list of events from a file's contents and stats.
    """
    if ' due ' in contents:
        # ex: DURATION due DEADLINE
        duration_str, end_date_str = contents.split(' due ')
        duration = _parse_duration(duration_str)

        tuple_result, flag = calendar.parse(end_date_str, creation_date)
        end_date = datetime(*tuple_result[:6])

        return (Event(name, None, duration, end_date),)

    elif contents.startswith('every') and ' from ' in contents:
        # ex: every DAY1[, DAY2 [and DAY3]] from HOUR to HOUR
        days, period = contents.replace('every ', '').split(' from ')
        return _create_recurring_events(name,
                                        days,
                                        period,
                                        creation_date,
                                        max_date)

    elif ' to ' in contents:
        # 'From' can be safely ignored from appointments.
        clean_contents = contents.replace('from ', '')
        # ex: [from] START to END or
        # ex: START_DATE from START_TIME to END_TIME
        start_date, end_date = _parse(clean_contents.split(' to '),
                                     creation_date)
        duration = end_date - start_date
        return (Event(name, start_date, duration, end_date),)

    else:
        raise Exception('Unexpected content in {}: {}'.format(name, contents))

