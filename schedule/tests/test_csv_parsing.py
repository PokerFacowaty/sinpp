from django.test import TestCase
from pathlib import Path
from datetime import datetime, timezone
from schedule.models import Event, Speedrun
from schedule.parse_schedule_csv import parse_oengus


class CSVParsingTestCase(TestCase):

    def setUp(self):
        ev_start = datetime(year=2022, month=2, day=12, hour=10,
                            tzinfo=timezone.utc)
        ev_end = datetime(year=2022, month=2, day=20, hour=3,
                          tzinfo=timezone.utc)
        ev = Event.objects.create(NAME="ESA Winter 2022",
                                  SHORT_TITLE="ESAW22",
                                  START_DATE_TIME=ev_start,
                                  END_DATE_TIME=ev_end)

        parse_oengus(Path(__file__).parent.resolve()
                     / "fixtures"
                     / "ESA-Win22-oengus.csv", ev)

    def test_first_run_time(self):
        event = Event.objects.get(SHORT_TITLE="ESAW22")
        first_run = Speedrun.objects.filter(EVENT=event).order_by(
                    "START_TIME")[0]
        time_to_compare = datetime(year=2022, month=2, day=12, hour=11,
                                   tzinfo=timezone.utc)
        self.assertEqual(first_run.START_TIME, time_to_compare)
