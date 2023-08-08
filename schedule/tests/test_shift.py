from django.test import TestCase
from schedule.models import Shift, Event, Role, Speedrun, Person
from datetime import datetime, timedelta, timezone


class ShiftTestCase(TestCase):
    # TODO:
    # - Check for proper VOLUNTEER, ROLE, EVENT
    # - Intermissions for run-based roles?

    def setUp(self):
        ev_start = datetime(year=2022, month=2, day=3, hour=14,
                            tzinfo=timezone.utc)
        ev_end = ev_start + timedelta(days=1)
        ev = Event.objects.create(NAME="GDQ2",
                                  SHORT_TITLE="GDQ2",
                                  START_DATE_TIME=ev_start,
                                  END_DATE_TIME=ev_end)
        tech = Role.objects.create(NAME="Tech",
                                   EVENT=ev,
                                   TYPE="HB")
        media = Role.objects.create(NAME="Social Media",
                                    EVENT=ev,
                                    TYPE="HB")
        prsn = Person.objects.create(NICKNAME="MyPerson")
        prsn.ROLES.set([tech, media])
        tech_shift = Shift.objects.create(
                     ROLE=tech, EVENT=ev,
                     START_DATE_TIME=ev_start + timedelta(hours=1),
                     END_DATE_TIME=ev_start + timedelta(hours=2))
        tech_shift.VOLUNTEER.set([prsn])

    def test_if_not_free(self):
        prsn = Person.objects.get(NICKNAME="MyPerson")
        start = (Event.objects.get(NAME="GDQ2").START_DATE_TIME
                 + timedelta(hours=1, minutes=30))
        end = (Event.objects.get(NAME="GDQ2").START_DATE_TIME
               + timedelta(hours=2, minutes=30))
        self.assertFalse(prsn.is_free(start, end))

    def test_if_free(self):
        prsn = Person.objects.get(NICKNAME="MyPerson")
        start = (Event.objects.get(NAME="GDQ2").START_DATE_TIME
                 + timedelta(hours=2, minutes=30))
        end = (Event.objects.get(NAME="GDQ2").START_DATE_TIME
               + timedelta(minutes=30))
        self.assertTrue(prsn.is_free(start, end))
