from django.test import TestCase
from django.utils import timezone
from schedule.models import Role, Event
from datetime import timedelta


class RoleTestCase(TestCase):

    def setUp(self):
        event_start_date = timezone.now()
        event_end_date = timezone.now() + timedelta(days=1)
        gtam = Event.objects.create(NAME="GTAMarathon 2027",
                                    SHORT_TITLE="GTAM27",
                                    START_DATE_TIME=event_start_date,
                                    END_DATE_TIME=event_end_date)
        Role.objects.create(NAME="Tech", EVENT=gtam)
        Role.objects.create(NAME="Fundraising", EVENT=gtam, VISIBILITY="PU",
                            TYPE="SB")

    def test_default_values_visibility(self):
        role = Role.objects.get(NAME="Tech")
        self.assertEqual(role.VISIBILITY, "RL")

    def test_default_values_type(self):
        role = Role.objects.get(NAME="Tech")
        self.assertTrue(role.TYPE, "HB")

    def test_non_default_values_visibility(self):
        role = Role.objects.get(NAME="Fundraising")
        self.assertEqual(role.VISIBILITY, "PU")

    def test_non_default_values_hour_based(self):
        role = Role.objects.get(NAME="Fundraising")
        self.assertTrue(role.TYPE, "SB")

    def test_proper_event(self):
        event = Event.objects.get(NAME="GTAMarathon 2027")
        role = Role.objects.get(NAME="Tech")
        self.assertEqual(role.EVENT, event)
