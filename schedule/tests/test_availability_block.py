from django.test import TestCase
from django.utils import timezone
from schedule.models import Event, AvailabilityBlock, Person, Role, Speedrun
from datetime import timedelta


class AvailabilityBlockTestCase(TestCase):
    # TODO:
    # - check if a Person is NOT avaiable when they shouldn't be
    def setUp(self):
        event_start_date = timezone.now()
        event_end_date = timezone.now() + timedelta(days=1)
        esaa = Event.objects.create(NAME="ESA Autumn 2028",
                                    SHORT_TITLE="ESAA2028",
                                    START_DATE_TIME=event_start_date,
                                    END_DATE_TIME=event_end_date)
        role = Role.objects.create(NAME="Social Media",
                                   EVENT=esaa)
        person = Person.objects.create(NICKNAME="Duncan")
        person.ROLES.set([role])
        avail_start = event_start_date + timedelta(minutes=30)
        avail_end = event_start_date + timedelta(hours=2)
        avail = AvailabilityBlock.objects.create(PERSON=person,
                                                 EVENT=esaa,
                                                 START_DATE_TIME=avail_start,
                                                 END_DATE_TIME=avail_end)
        avail2_start = event_start_date + timedelta(hours=4)
        avail2_end = event_start_date + timedelta(hours=5)
        avail2 = AvailabilityBlock.objects.create(PERSON=person,
                                                  EVENT=esaa,
                                                  START_DATE_TIME=avail2_start,
                                                  END_DATE_TIME=avail2_end)
        run_start = event_start_date + timedelta(hours=1)
        run_end = event_start_date + timedelta(hours=1, minutes=30)
        run = Speedrun.objects.create(EVENT=esaa,
                                      GAME="GTA: Vice City",
                                      START_TIME=run_start,
                                      END_TIME=run_end)

    def test_check_if_available_manually(self):
        run = Speedrun.objects.get(GAME="GTA: Vice City")
        person = Person.objects.get(NICKNAME="Duncan")
        # Not 100% about this since it assumes a single block but this can
        # be changed later
        avail = AvailabilityBlock.objects.get(PERSON=person)
        # NOTE: the only way to ensure proper time arithmetic is by using
        # PostgresSQL as the database
        # https://docs.djangoproject.com/en/4.2/ref/models/fields/#durationfield
        self.assertTrue(((run.START_TIME - avail.START_DATE_TIME)
                         >= run.EVENT.TIME_SAFETY_MARGIN
                         and (avail.END_DATE_TIME - run.END_TIME)
                         >= run.EVENT.TIME_SAFETY_MARGIN))

    def test_check_if_available_function(self):
        run = Speedrun.objects.get(GAME="GTA: Vice City")
        person = Person.objects.get(NICKNAME="Duncan")
        # Not 100% about this since it assumes a single block but this can
        # be changed later
        self.assertTrue(person.is_available(run.START_TIME, run.END_TIME,
                                            run.EVENT))

    def test_check_if_not_available_manually(self):
        run = Speedrun.objects.get(GAME="GTA: Vice City")
        person = Person.objects.get(NICKNAME="Duncan")
        avail_start = run.EVENT.START_DATE_TIME + timedelta(hours=4)
        avail = AvailabilityBlock.objects.get(PERSON=person,
                                              START_DATE_TIME=avail_start)
        self.assertFalse((run.START_TIME - avail.START_DATE_TIME)
                         >= run.EVENT.TIME_SAFETY_MARGIN
                         and (avail.END_DATE_TIME - run.END_TIME)
                         >= run.EVENT.TIME_SAFETY_MARGIN)
