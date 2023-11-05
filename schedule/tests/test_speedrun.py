from django.test import TestCase
from django.utils import timezone
from schedule.models import Event, Speedrun, Person
from datetime import timedelta, datetime


class SpeedrunTestCase(TestCase):

    def setUp(self):
        event_start_date = datetime(year=2020, month=4, day=7, hour=11,
                                    tzinfo=timezone.utc)
        event_end_date = event_start_date + timedelta(days=1)
        ev = Event.create(NAME="GSPS 2026",
                          SLUG="GSPS26",
                          START_DATE_TIME=event_start_date,
                          END_DATE_TIME=event_end_date)
        ev.save()

        peoples_names = ["Alice", "Bob", "Candy"]
        peoples_pronouns = ["", "She/They", ""]
        i = 0
        while i < 3:
            Person.objects.create(NICKNAME=peoples_names[i],
                                  PRONOUNS=peoples_pronouns[i])
            i += 1

        run_start_time = event_start_date + timedelta(minutes=1)
        estimate = timedelta(minutes=5)
        alice = Person.objects.get(NICKNAME="Alice")
        candy = Person.objects.get(NICKNAME="Candy")
        Speedrun.objects.create(EVENT=Event.objects.get(SLUG="GSPS26"),
                                GAME="GTA IV", START_DATE_TIME=run_start_time,
                                ESTIMATE=estimate)
        iv = Speedrun.objects.get(GAME="GTA IV")
        iv.VOLUNTEERS_ENGAGED.add(alice)
        iv.VOLUNTEERS_ENGAGED.add(candy)

    def test_speedrun_has_calculated_end_time(self):
        run = Speedrun.objects.get(GAME="GTA IV")
        # NOTE: the only way to ensure proper time arithmetic is by using
        # PostgresSQL as the database
        # https://docs.djangoproject.com/en/4.2/ref/models/fields/#durationfield
        self.assertEqual(run.END_DATE_TIME, run.START_DATE_TIME + run.ESTIMATE)

    def test_speedrun_has_volunteer_one_engaged(self):
        run = Speedrun.objects.get(GAME="GTA IV")
        alice = Person.objects.get(NICKNAME="Alice")
        self.assertIn(alice, run.VOLUNTEERS_ENGAGED.all())

    def test_speedrun_has_volunteer_two_engaged(self):
        run = Speedrun.objects.get(GAME="GTA IV")
        candy = Person.objects.get(NICKNAME="Candy")
        self.assertIn(candy, run.VOLUNTEERS_ENGAGED.all())
