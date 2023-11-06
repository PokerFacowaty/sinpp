from django.test import TestCase
from django.utils import timezone
from schedule.models import Role, Event
from datetime import timedelta, datetime


class RoleTestCase(TestCase):

    def setUp(self):
        event_start_date = datetime(year=2020, month=4, day=7, hour=11,
                                    tzinfo=timezone.utc)
        event_end_date = event_start_date + timedelta(days=1)
        gtam = Event.create(NAME="GTAMarathon 2027",
                            SLUG="GTAM27",
                            START_DATE_TIME=event_start_date,
                            END_DATE_TIME=event_end_date)
        gtam.save()
        Role.objects.create(NAME="Tech", EVENT=gtam)
        Role.objects.create(NAME="Fundraising", EVENT=gtam)
