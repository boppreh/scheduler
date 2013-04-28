from datetime import datetime, timedelta
from unittest import TestCase, main
from scheduler import get_first_slot, Event

class TestGetFirstSlot(TestCase):
    def setUp(self):
        self.min_date = datetime.now()
        self.hour = timedelta(0, 3600)
        self.max_date = self.min_date + 1000 * self.hour

    def test_empty_events(self):
        result = get_first_slot(self.min_date, [], None)
        self.assertEqual(result, self.min_date)

    def test_single_event(self):
        events = [Event('', self.min_date, 0, self.min_date)]
        event = Event('', self.min_date, self.hour, self.min_date + self.hour)

        result = get_first_slot(self.min_date, events, event)
        self.assertEqual(result, self.min_date)

    def test_single_not_fit(self):
        events = [Event('', self.min_date, 0, self.max_date)]
        event = Event('', self.min_date, self.hour, self.min_date + self.hour)

        result = get_first_slot(self.min_date, events, event)
        self.assertEqual(result, self.max_date)


if __name__ == '__main__':
    main()
