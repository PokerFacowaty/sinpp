from django.test import TestCase
from schedule.models import Event, Speedrun
from datetime import datetime, timedelta


class SpeedrunTestCase(TestCase):
    # TODO:
    # - Check for listing volunteers involved in the run
    # - Check for listing volunteer shifts, both run based and hour based
    # - Add an option to provide START + END and calculate ESTIMATE?
    # (add + test)

    def setUp(self):
        start_date = datetime.now()
        end_date = datetime.now() + timedelta(days=1)
        Event.objects.create(NAME="GSPS 2026",
                             SHORT_TITLE="GSPS26",
                             START_DATE_TIME=start_date,
                             END_DATE_TIME=end_date)
        run_start_time = start_date + timedelta(minutes=1)
        estimate = timedelta(minutes=5)
        Speedrun.objects.create(EVENT=Event.objects.get(NAME="GSPS 2026"),
                                GAME="GTA IV", START_TIME=run_start_time,
                                ESTIMATE=estimate)

    def test_speedrun_has_calculated_end_time(self):
        run = Speedrun.objects.get(GAME="GTA IV")
        self.assertEqual(run.END_TIME, run.START_TIME + run.ESTIMATE)
