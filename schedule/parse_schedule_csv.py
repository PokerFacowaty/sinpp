import csv
from pathlib import Path
from models import Event, Speedrun, Intermission
from datetime import datetime as dt
from datetime import time


def parse_oengus(filepath: str, event: Event):
    with open(Path(filepath)) as cf:
        rdr = csv.DictReader(cf)

        for row in rdr:
            # NOTE: Oengus estimates and setup times are not ISO 8601
            # because of no trailing zeros on hours, so that's why I'm parsing
            # them manually instead of using time.fromisoformat.
            # They also need to be sliced because of timezone names added
            # at the end (e.x. "2022-02-12T16:37:00+01:00[Europe/Warsaw]")

            run_start = dt.fromisoformat(row["time"][:25])
            estimate = [int(x) for x in row["estimate"].split(":")]
            estimate = time(hour=estimate[0],
                            minute=estimate[1],
                            second=estimate[2])
            inter_dur = [int(y) for y in row["setup_time"].split(":")]
            inter_dur = time(hour=inter_dur[0],
                             minute=inter_dur[1],
                             second=inter_dur[2])

            Speedrun(EVENT=event,
                     GAME=row["game"],
                     CATEGORY=row["category"],
                     START_TIME=run_start,
                     ESTIMATE=estimate)

            Intermission(EVENT=event,
                         START_TIME=run_start + estimate,
                         DURATION=inter_dur)
