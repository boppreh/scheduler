"""
Module for arranging a list of events in a consistent schedule.
"""
from datetime import datetime

def _get_first_slot(min_date, events, event_to_fit):
    """
    Given a list of fixed events, finds a continuous time slot with a given
    duration, starting at time min_date.
    """
    if not events:
        return min_date

    sorted_events = sorted(events, key=lambda e: e.start_date)

    # Fit at the beginning, before any other event.
    if sorted_events[0].start_date - min_date > event_to_fit.duration:
        return min_date

    for i in range(len(sorted_events) - 1):
        # Takes pairs of events.
        before, after = sorted_events[i:i+2]

        available_space = after.start_date - before.end_date

        if available_space > event_to_fit.duration:
            return before.end_date

    # No space between events, fit after the last event.
    return sorted_events[-1].end_date

def schedule(events):
    """
    Given a list of partial events (missing start dates), returns events with
    definite start date, duration and end date, respecting deadlines and
    durations, without overlap.
    """
    # Fixed = has start and end date, appointment.
    # Free = has duration and deadline, a task.
    fixed, free = [], []
    for event in events:
        # An event must be either an appointment or a task.
        assert (event.start_date or event.duration) and event.end_date

        if event.start_date:
            fixed.append(event)
        elif event.duration:
            free.append(event)

    # Sorts tasks by deadline.
    free.sort(key=lambda e: e.end_date)
    while free:
        event = free.pop(0)
        # Find a slot for this task.
        event.start_date = _get_first_slot(datetime.now(), fixed, event)
        new_end_date = event.start_date + event.duration

        if new_end_date > event.end_date:
            raise Exception('Could not fit event %s in schedule.' % (event))

        # Replace the deadline with the real end date.
        event.end_date = new_end_date
        # Uses it as an appointment to avoid conflict between the next tasks.
        fixed.append(event)

    return sorted(fixed, key=lambda e: e.start_date)
