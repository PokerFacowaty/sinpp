from django.test import TestCase
from django.utils import timezone
from schedule.models import Event, AvailabilityBlock, Person, Role, Speedrun
from datetime import timedelta


class AvailabilityBlockTestCase(TestCase):

    def setUp(self):
        event_start_date = timezone.now()
        event_end_date = timezone.now() + timedelta(days=1)
        esaa = Event.create(NAME="ESA Autumn 2028",
                                    SLUG="ESAA2028",
                                    START_DATE_TIME=event_start_date,
                                    END_DATE_TIME=event_end_date)
        esaa.save()
        role = Role.objects.create(NAME="Social Media",
                                   EVENT=esaa)
        # person has two blocks, one is during the run and the other is
        # outside of it.
        # person2 has a single block that's outside the run.
        person = Person.objects.create(NICKNAME="Duncan")
        person2 = Person.objects.create(NICKNAME="Elaine")
        person.ROLES.set([role])
        person2.ROLES.set([role])
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
        p2_av_start = event_start_date + timedelta(hours=5)
        p2_av_end = event_start_date + timedelta(hours=6)
        p2_avail = AvailabilityBlock.objects.create(
                                        PERSON=person2,
                                        EVENT=esaa,
                                        START_DATE_TIME=p2_av_start,
                                        END_DATE_TIME=p2_av_end)
        run_start = event_start_date + timedelta(hours=1)
        run_end = event_start_date + timedelta(hours=1, minutes=30)
        run = Speedrun.objects.create(EVENT=esaa,
                                      GAME="GTA: Vice City",
                                      START_DATE_TIME=run_start,
                                      END_DATE_TIME=run_end)

    def test_check_if_available_manually(self):
        run = Speedrun.objects.get(GAME="GTA: Vice City")
        avail_start = run.EVENT.START_DATE_TIME + timedelta(minutes=30)
        person = Person.objects.get(NICKNAME="Duncan")
        margin = Role.objects.get(NAME="Social Media").TIME_SAFETY_MARGIN
        avail = AvailabilityBlock.objects.get(PERSON=person,
                                              START_DATE_TIME=avail_start)
        # NOTE: the only way to ensure proper time arithmetic is by using
        # PostgresSQL as the database
        # https://docs.djangoproject.com/en/4.2/ref/models/fields/#durationfield
        self.assertTrue(((run.START_DATE_TIME - avail.START_DATE_TIME)
                         >= margin
                         and (avail.END_DATE_TIME - run.END_DATE_TIME)
                         >= margin))

    def test_check_if_available_function(self):
        run = Speedrun.objects.get(GAME="GTA: Vice City")
        person = Person.objects.get(NICKNAME="Duncan")
        role = Role.objects.get(NAME="Social Media")
        # Not 100% about this since it assumes a single block but this can
        # be changed later
        self.assertTrue(person.is_available(run.START_DATE_TIME, run.END_DATE_TIME,
                                            role))

    def test_check_if_not_available_manually(self):
        run = Speedrun.objects.get(GAME="GTA: Vice City")
        person = Person.objects.get(NICKNAME="Duncan")
        margin = Role.objects.get(NAME="Social Media").TIME_SAFETY_MARGIN
        avail_start = run.EVENT.START_DATE_TIME + timedelta(hours=4)
        avail = AvailabilityBlock.objects.get(PERSON=person,
                                              START_DATE_TIME=avail_start)
        self.assertFalse((run.START_DATE_TIME - avail.START_DATE_TIME)
                         >= margin
                         and (avail.END_DATE_TIME - run.END_DATE_TIME)
                         >= margin)

    def test_check_if_not_available_function(self):
        run = Speedrun.objects.get(GAME="GTA: Vice City")
        person = Person.objects.get(NICKNAME="Elaine")
        role = Role.objects.get(NAME="Social Media")
        self.assertFalse(person.is_available(run.START_DATE_TIME, run.END_DATE_TIME,
                                             role))
