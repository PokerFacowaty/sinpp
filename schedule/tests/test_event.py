from django.test import TestCase
from django.utils import timezone
from schedule.models import Event
from datetime import timedelta


class EventTestCase(TestCase):
    # TODO:
    # - Events generating a short title if not provided (added + tested)
    # - Event has proper dates
    # - Event parses TIME_SAFETY_MARGIN correctly from string? (if that should
    # happen since I'm not sure)
    def setUp(self):
        start_date = timezone.now()
        end_date = timezone.now() + timedelta(days=1)
        Event.objects.create(NAME="GSPS 2026",
                             SHORT_TITLE="GSPS26",
                             START_DATE_TIME=start_date,
                             END_DATE_TIME=end_date)

    def test_event_has_name(self):
        gsps = Event.objects.get(SHORT_TITLE="GSPS26")
        self.assertEqual(gsps.NAME, "GSPS 2026")
