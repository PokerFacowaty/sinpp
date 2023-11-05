from django.test import TestCase
from django.utils import timezone
from schedule.models import Event
from datetime import timedelta
from django.contrib.auth.models import Group


class EventTestCase(TestCase):
    def setUp(self):
        start_date = timezone.now()
        end_date = timezone.now() + timedelta(days=1)
        ev = Event.create(NAME="GSPS 2026",
                          SLUG="GSPS26",
                          START_DATE_TIME=start_date,
                          END_DATE_TIME=end_date)
        ev.save()

    def test_proper_group_was_made(self):
        self.assertTrue(Group.objects.filter(name="GSPS26 Staff"))
