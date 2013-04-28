from scheduler import get_full_schedule
from win32api import *
from win32gui import *
from win32con import *
import win32ui
import sys, os
import subprocess
from datetime import datetime, timedelta
from time import sleep

def Oget_events_list(events):
    now = datetime.now().replace(minute=0, second=0, microsecond=0)

    offset = 0
    while events[offset].end_date < now:
        offset += 1

    result = []
    now = min(now, events[0].start_date)
    tomorrow = now.replace(hour=0) + timedelta(days=1)
    hour = timedelta(hours=1)

    while now < tomorrow:
        event = events[offset]

        result.append(now.strftime('%H:%M') + ' ')
        if event.start_date <= now <= event.end_date:
            result.append(event.name)
        else:
            result.append('-')
        result.append('\n')

        now += hour
        if event.end_date < now:
            offset += 1

    return ''.join(result)

def get_events_list(events):
    result = []
    tomorrow = datetime.now().replace(hour=0, minute=0) + timedelta(days=1)
    for event in events:
        if event.start_date < tomorrow:
            start = event.start_date.strftime('%H:%M')
            end = event.end_date.strftime('%H:%M')
            result.append('{}: {} - {} ({})'.format(event.name,
                                                    start,
                                                    end,
                                                    event.duration))
    return '\n'.join(result)

def sleep_until_event_start(event):
    """
    Suspends execution of this thread until the given event has started.
    """
    time_difference = event.start_date - datetime.now()
    sleep(max(0, time_difference.total_seconds()))

def get_message(event):
    """
    Returns a message detailing the start time, end time and duration of the
    given event.
    """
    start = event.start_date.strftime('%H:%M')
    end = event.end_date.strftime('%H:%M')

    duration = round(event.duration.total_seconds() / 360.0) / 10.0
    if duration >= 1:
        duration_string = str(duration) + ' hours'
    else:
        duration_string = str(round(duration * 60)) + ' minutes'

    return '{}  -  {}  ({})'.format(start, end, duration_string)

def process_events(events):
    """
    Infinite loop for updating the notifications from a list of events.
    """
    offset = 0
    while True:
        event = events[offset]
        sleep_until_event_start(event)
        notify(event.name, get_message(event))
        offset += 1

if __name__ == '__main__':
    try:
        events = get_full_schedule('./events/')
    except Exception as e:
        win32ui.MessageBox(str(e), 'Error', 0)
        exit()

    if not events:
        exit()

    from background import tray, quit, notify

    def restart():
        this_path = os.path.join(os.getcwd(), __file__)
        subprocess.check_call('pythonw "{}"'.format(this_path), shell=True)
        quit()

    def show_next_events():
        win32ui.MessageBox(get_events_list(events), 'Next events', 0)

    tray('Schedule Notifier', 'calendar.ico', [show_next_events, restart, quit])

    # Wait for the tray icon to be ready, in case there's an event right now.
    sleep(1)
    
    process_events(events)
