import csv
from pathlib import Path
from schedule.models import Event, Speedrun, Intermission
from datetime import datetime as dt
from datetime import timedelta
from django.conf import settings
import uuid


def handle_uploaded_file(f, type: str):
    # The + ".csv" part is a hack for testing, obviously
    # TODO: handle that when I stop testing
    filepath = Path(settings.MEDIA_ROOT / (str(uuid.uuid4()) + ".csv"))
    if not filepath.parent.exists():
        filepath.parent.mkdir(parents=True)
    with open(filepath, "wb+") as destination:
        for chunk in f.chunks():
            destination.write(chunk)
    return filepath


def parse_oengus(filepath: Path, event: Event, room=None):
    print(filepath, event)
    with open(filepath) as cf:
        rdr = csv.DictReader(cf)

        for row in rdr:
            # NOTE: Oengus estimates and setup times are not ISO 8601
            # because of no trailing zeros on hours, so that's why I'm parsing
            # them manually instead of using time.fromisoformat.
            # They also need to be sliced because of timezone names added
            # at the end (e.x. "2022-02-12T16:37:00+01:00[Europe/Warsaw]")

            run_start = dt.fromisoformat(row["time"][:25])
            estimate = [int(x) for x in row["estimate"].split(":")]
            estimate = timedelta(hours=estimate[0],
                                 minutes=estimate[1],
                                 seconds=estimate[2])
            inter_dur = [int(y) for y in row["setup_time"].split(":")]
            inter_dur = timedelta(hours=inter_dur[0],
                                  minutes=inter_dur[1],
                                  seconds=inter_dur[2])

            Speedrun.objects.create(EVENT=event,
                                    ROOM=room,
                                    GAME=row["game"],
                                    CATEGORY=row["category"],
                                    START_DATE_TIME=run_start,
                                    ESTIMATE=estimate)

            Intermission.objects.create(EVENT=event,
                                        ROOM=room,
                                        START_DATE_TIME=run_start + estimate,
                                        DURATION=inter_dur)
