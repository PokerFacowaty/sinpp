from django.test import TestCase
from django.utils import timezone
from schedule.models import (Event, AvailabilityBlock, Person, Role, Speedrun,
                             Shift, Room)
from datetime import timedelta, datetime
from django.contrib.auth.models import Group, User


class TestEvent(TestCase):
    def setUp(self):
        self.user = User.objects.create_user("notverysuper", "", "password1")
        start_date = datetime(year=2020, month=4, day=7, hour=11,
                              tzinfo=timezone.utc)
        end_date = start_date + timedelta(days=1)
        self.ev = Event.create(NAME="GSPS 2026", SLUG="GSPS26",
                               START_DATE_TIME=start_date,
                               END_DATE_TIME=end_date)

    def test_event_proper_group_was_made(self):
        self.assertTrue(Group.objects.filter(name="GSPS26 Staff"))

    def test_event_str(self):
        self.assertEqual(str(self.ev), self.ev.NAME)


class TestRoom(TestCase):

    def setUp(self):
        self.user = User.objects.create_user("notverysuper", "", "password1")
        start_date = datetime(year=2020, month=4, day=7, hour=11,
                              tzinfo=timezone.utc)
        end_date = start_date + timedelta(days=1)
        self.ev = Event.create(NAME="GSPS 2026", SLUG="GSPS26",
                               START_DATE_TIME=start_date,
                               END_DATE_TIME=end_date)
        self.rm = Room.objects.add(EVENT=self.ev, NAME="Stream 1", SLUG="S1")

    def test_room_str(self):
        self.assertEqual(str(self.rm), self.rm.NAME + f' ({self.ev})')


class TestSpeedrun(TestCase):

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


class TestIntermission(TestCase):
    pass


class TestShift(TestCase):

    def setUp(self):
        ev_start = datetime(year=2022, month=2, day=3, hour=14,
                            tzinfo=timezone.utc)
        ev_end = ev_start + timedelta(days=1)
        ev = Event.create(NAME="GDQ2",
                          SLUG="GDQ2",
                          START_DATE_TIME=ev_start,
                          END_DATE_TIME=ev_end)
        ev.save()
        tech = Role.objects.create(NAME="Tech",
                                   EVENT=ev)
        media = Role.objects.create(NAME="Social Media",
                                    EVENT=ev)
        prsn = Person.objects.create(NICKNAME="MyPerson")
        prsn.ROLES.set([tech, media])
        tech_shift = Shift.objects.create(
                     ROLE=tech, EVENT=ev,
                     START_DATE_TIME=ev_start + timedelta(hours=1),
                     END_DATE_TIME=ev_start + timedelta(hours=2))
        tech_shift.VOLUNTEERS.set([prsn])

    def test_if_busy(self):
        prsn = Person.objects.get(NICKNAME="MyPerson")
        start = (Event.objects.get(SLUG="GDQ2").START_DATE_TIME
                 + timedelta(hours=1, minutes=30))
        end = (Event.objects.get(SLUG="GDQ2").START_DATE_TIME
               + timedelta(hours=2, minutes=30))
        self.assertTrue(prsn.is_busy(start, end))

    def test_if_not_busy(self):
        prsn = Person.objects.get(NICKNAME="MyPerson")
        start = (Event.objects.get(SLUG="GDQ2").START_DATE_TIME
                 + timedelta(hours=2, minutes=30))
        end = (Event.objects.get(NAME="GDQ2").START_DATE_TIME
               + timedelta(minutes=30))
        self.assertFalse(prsn.is_busy(start, end))


class TestPerson(TestCase):
    pass


class TestAvailabilityBlock(TestCase):

    def setUp(self):
        event_start_date = datetime(year=2020, month=4, day=7, hour=11,
                                    tzinfo=timezone.utc)
        event_end_date = event_start_date + timedelta(days=1)
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
        AvailabilityBlock.objects.create(PERSON=person,
                                         EVENT=esaa,
                                         START_DATE_TIME=avail_start,
                                         END_DATE_TIME=avail_end)
        avail2_start = event_start_date + timedelta(hours=4)
        avail2_end = event_start_date + timedelta(hours=5)
        AvailabilityBlock.objects.create(PERSON=person,
                                         EVENT=esaa,
                                         START_DATE_TIME=avail2_start,
                                         END_DATE_TIME=avail2_end)
        p2_av_start = event_start_date + timedelta(hours=5)
        p2_av_end = event_start_date + timedelta(hours=6)
        AvailabilityBlock.objects.create(
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
        sh = Shift.objects.create(ROLE=role, EVENT=esaa,
                                  START_DATE_TIME=run.START_DATE_TIME,
                                  END_DATE_TIME=run.END_DATE_TIME)
        sh.VOLUNTEERS.add(person2)

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
        self.assertTrue(person.is_available(run.START_DATE_TIME,
                                            run.END_DATE_TIME,
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
        self.assertFalse(person.is_available(run.START_DATE_TIME,
                                             run.END_DATE_TIME,
                                             role))

    def test_check_if_busy_function(self):
        run = Speedrun.objects.get(GAME="GTA: Vice City")
        st = run.START_DATE_TIME - timedelta(hours=1)
        end = run.END_DATE_TIME + timedelta(hours=1)
        person = Person.objects.get(NICKNAME="Elaine")
        self.assertTrue(person.is_busy(st, end))

    def test_check_if_not_busy_function(self):
        run = Speedrun.objects.get(GAME="GTA: Vice City")
        st = run.START_DATE_TIME
        end = run.END_DATE_TIME
        person = Person.objects.get(NICKNAME="Duncan")
        self.assertFalse(person.is_busy(st, end))


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
