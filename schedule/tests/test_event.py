from django.test import TestCase
from schedule.models import Event
from datetime import datetime, timedelta


class EventTestCase(TestCase):
    # TODO:
    # - Events generating a short title if not provided (added + tested)
    # - Event has proper dates
    def setUp(self):
        start_date = datetime.now()
        end_date = datetime.now() + timedelta(days=1)
        Event.objects.create(NAME="GSPS 2026",
                             SHORT_TITLE="GSPS26",
                             START_DATE_TIME=start_date,
                             END_DATE_TIME=end_date)

    def test_event_has_name(self):
        gsps = Event.objects.get(SHORT_TITLE="GSPS26")
        self.assertEqual(gsps.NAME, "GSPS 2026")
