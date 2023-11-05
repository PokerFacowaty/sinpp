from django.test import TestCase
from pathlib import Path
from datetime import datetime, timezone
from schedule.models import Event, Speedrun, Intermission
from schedule.parse_schedule_csv import parse_oengus


class CSVParsingTestCase(TestCase):

    def setUp(self):
        ev_start = datetime(year=2022, month=2, day=12, hour=10,
                            tzinfo=timezone.utc)
        ev_end = datetime(year=2022, month=2, day=20, hour=3,
                          tzinfo=timezone.utc)
        ev = Event.create(NAME="ESA Winter 2022",
                          SLUG="ESAW22",
                          START_DATE_TIME=ev_start,
                          END_DATE_TIME=ev_end)
        ev.save()

        parse_oengus(Path(__file__).parent.resolve()
                     / "fixtures"
                     / "ESA-Win22-oengus.csv", ev)

    def test_first_run_time(self):
        event = Event.objects.get(SLUG="ESAW22")
        first_run = Speedrun.objects.filter(EVENT=event).order_by(
                    "START_DATE_TIME")[0]
        time_to_compare = datetime(year=2022, month=2, day=12, hour=11,
                                   tzinfo=timezone.utc)
        self.assertEqual(first_run.START_DATE_TIME, time_to_compare)

    def test_last_run_time(self):
        event = Event.objects.get(SLUG="ESAW22")
        last_run = Speedrun.objects.filter(EVENT=event).order_by(
            "START_DATE_TIME").reverse()[0]
        time_to_compare = datetime(year=2022, month=2, day=20, hour=0,
                                   minute=25, tzinfo=timezone.utc)
        self.assertEqual(last_run.START_DATE_TIME, time_to_compare)

    def test_some_intermission_start(self):
        event = Event.objects.get(SLUG="ESAW22")
        speedrun = Speedrun.objects.get(EVENT=event, GAME="Donut County")
        inter = Intermission.objects.filter(
                START_DATE_TIME__gt=speedrun.START_DATE_TIME)[0]
        time_to_compare = datetime(year=2022, month=2, day=15, hour=12,
                                   minute=35, tzinfo=timezone.utc)
        self.assertEqual(inter.START_DATE_TIME, time_to_compare)

    def test_some_other_intermission_end(self):
        event = Event.objects.get(SLUG="ESAW22")
        speedrun = Speedrun.objects.get(EVENT=event, GAME="Paint the Town Red")
        inter = Intermission.objects.filter(
                START_DATE_TIME__gt=speedrun.START_DATE_TIME)[0]
        time_to_compare = datetime(year=2022, month=2, day=14, hour=15,
                                   minute=35, tzinfo=timezone.utc)
        self.assertEqual(inter.END_DATE_TIME, time_to_compare)
