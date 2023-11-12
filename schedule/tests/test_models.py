from django.test import TestCase
from django.utils import timezone
from schedule.models import (Event, AvailabilityBlock, Person, Role, Speedrun,
                             Shift, Room, Intermission)
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
        self.ev.save()
        self.rm = Room.objects.create(EVENT=self.ev,
                                      NAME="Stream 1",
                                      SLUG="S1")

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

        iv_start_time = event_start_date + timedelta(minutes=1)
        iv_estimate = timedelta(minutes=5)
        self.alice = Person.objects.get(NICKNAME="Alice")
        self.candy = Person.objects.get(NICKNAME="Candy")
        self.iv = Speedrun.objects.create(EVENT=ev,
                                          GAME="GTA IV",
                                          START_DATE_TIME=iv_start_time,
                                          ESTIMATE=iv_estimate)
        self.iv.VOLUNTEERS_ENGAGED.add(self.alice)
        self.iv.VOLUNTEERS_ENGAGED.add(self.candy)

        v_start_time = event_start_date + timedelta(hours=1)
        v_end_time = v_start_time + timedelta(hours=5)
        self.rm = Room.objects.create(NAME="Stream 1", EVENT=ev)
        self.v = Speedrun.objects.create(EVENT=ev,
                                         GAME="GTA V",
                                         START_DATE_TIME=v_start_time,
                                         END_DATE_TIME=v_end_time,
                                         ROOM=self.rm)

    def test_speedrun_has_calculated_end_time(self):
        # NOTE: the only way to ensure proper time arithmetic is by using
        # PostgresSQL as the database
        # https://docs.djangoproject.com/en/4.2/ref/models/fields/#durationfield
        self.assertEqual(self.iv.END_DATE_TIME,
                         self.iv.START_DATE_TIME + self.iv.ESTIMATE)

    def test_speedrun_has_calulcated_estimate(self):
        self.assertEqual(self.v.ESTIMATE,
                         self.v.END_DATE_TIME - self.v.START_DATE_TIME)

    def test_speedrun_has_volunteer_one_engaged(self):
        self.assertIn(self.alice, self.iv.VOLUNTEERS_ENGAGED.all())

    def test_speedrun_has_volunteer_two_engaged(self):
        self.assertIn(self.candy, self.iv.VOLUNTEERS_ENGAGED.all())

    def test_speedrun_str_no_room_no_category(self):
        self.assertEqual(str(self.iv), "GTA IV (GSPS 2026)")

    def test_speedrun_str_no_room_category(self):
        self.iv.CATEGORY = "Any%"
        self.assertEqual(str(self.iv), "GTA IV [Any%] (GSPS 2026)")

    def test_speedrun_str_room_no_category(self):
        self.assertEqual(str(self.v), f"GTA V ({self.rm})")

    def test_speedrun_str_room_category(self):
        self.v.CATEGORY = "100%"
        self.assertEqual(str(self.v), f"GTA V [100%] ({self.rm})")


class TestIntermission(TestCase):

    def setUp(self):
        self.user = User.objects.create_user("notverysuper", "", "password1")

        start_date = datetime(year=2020, month=4, day=7, hour=11,
                              tzinfo=timezone.utc)
        end_date = start_date + timedelta(days=1)
        self.ev = Event.create(NAME="GSPS 2026", SLUG="GSPS26",
                               START_DATE_TIME=start_date,
                               END_DATE_TIME=end_date)
        self.ev.save()

        self.rm = Room.objects.create(EVENT=self.ev,
                                      NAME="Stream 2",
                                      SLUG="S2")

        i1_start = self.ev.START_DATE_TIME + timedelta(hours=1)
        i1_end = i1_start + timedelta(minutes=15)
        self.interm1 = Intermission.objects.create(START_DATE_TIME=i1_start,
                                                   END_DATE_TIME=i1_end,
                                                   EVENT=self.ev,
                                                   ROOM=self.rm)

        i2_start = self.ev.START_DATE_TIME + timedelta(hours=2)
        i2_duration = timedelta(minutes=15)
        self.interm2 = Intermission.objects.create(START_DATE_TIME=i2_start,
                                                   DURATION=i2_duration,
                                                   EVENT=self.ev)

    def test_interm_has_calculated_end_time(self):
        self.assertEqual(self.interm1.END_DATE_TIME,
                         self.interm1.START_DATE_TIME + self.interm1.DURATION)

    def test_interm_has_calculated_duration(self):
        self.assertEqual(self.interm1.DURATION,
                         self.interm1.END_DATE_TIME
                         - self.interm1.START_DATE_TIME)

    def test_interm_str_room(self):
        self.assertEqual(str(self.interm1),
                         f"Intermission @ {self.interm1.START_DATE_TIME}"
                         + f" ({self.rm})")

    def test_interm_str_no_room(self):
        self.assertEqual(str(self.interm2),
                         f"Intermission @ {self.interm2.START_DATE_TIME}"
                         + f" ({self.ev})")


class TestShift(TestCase):

    def setUp(self):
        ev_start = datetime(year=2022, month=2, day=3, hour=14,
                            tzinfo=timezone.utc)
        ev_end = ev_start + timedelta(days=1)
        self.ev = Event.create(NAME="GDQ2",
                               SLUG="GDQ2",
                               START_DATE_TIME=ev_start,
                               END_DATE_TIME=ev_end)
        self.ev.save()
        self.rm = Room.objects.create(EVENT=self.ev,
                                      NAME="Main Stream",
                                      SLUG="MS")
        tech = Role.objects.create(NAME="Tech",
                                   EVENT=self.ev)
        media = Role.objects.create(NAME="Social Media",
                                    EVENT=self.ev)
        prsn = Person.objects.create(NICKNAME="MyPerson")
        prsn.ROLES.set([tech, media])
        self.tech_shift = Shift.objects.create(
                          ROLE=tech, EVENT=self.ev,
                          START_DATE_TIME=ev_start + timedelta(hours=1),
                          END_DATE_TIME=ev_start + timedelta(hours=2))
        self.tech_shift.VOLUNTEERS.set([prsn])

    def test_shift_str_room(self):
        self.tech_shift.ROOM = self.rm
        nicknames = ", ".join([x.NICKNAME
                               for x in self.tech_shift.VOLUNTEERS.all()])
        self.assertEqual(str(self.tech_shift),
                         f"{nicknames}@ {self.tech_shift.START_DATE_TIME}"
                         + f" ({str(self.rm)})")

    def test_shift_str_no_room(self):
        nicknames = ", ".join([x.NICKNAME
                               for x in self.tech_shift.VOLUNTEERS.all()])
        self.assertEqual(str(self.tech_shift),
                         f"{nicknames}@ {self.tech_shift.START_DATE_TIME}"
                         + f" ({str(self.ev)})")


class TestPerson(TestCase):

    def setUp(self):
        ev_start = datetime(year=2022, month=2, day=3, hour=14,
                            tzinfo=timezone.utc)
        ev_end = ev_start + timedelta(days=1)
        self.ev = Event.create(NAME="GDQ2",
                               SLUG="GDQ2",
                               START_DATE_TIME=ev_start,
                               END_DATE_TIME=ev_end)
        self.ev.save()

        self.tech = Role.objects.create(NAME="Tech",
                                        EVENT=self.ev)
        self.prsn = Person.objects.create(NICKNAME="MyPerson")
        self.prsn.ROLES.set([self.tech])

        # Available for the tech shift
        avail1_start = ev_start
        avail1_end = ev_start + timedelta(hours=3)
        self.avail1 = AvailabilityBlock.objects.create(
                                                PERSON=self.prsn,
                                                EVENT=self.ev,
                                                START_DATE_TIME=avail1_start,
                                                END_DATE_TIME=avail1_end)
        self.tech_shift = Shift.objects.create(
                          ROLE=self.tech, EVENT=self.ev,
                          START_DATE_TIME=ev_start + timedelta(hours=1),
                          END_DATE_TIME=ev_start + timedelta(hours=2))
        self.tech_shift.VOLUNTEERS.set([self.prsn])

    def test_if_available(self):
        self.assertTrue(self.prsn.is_available(self.tech_shift.START_DATE_TIME,
                                               self.tech_shift.END_DATE_TIME,
                                               self.tech))

    def test_if_not_available(self):
        st = self.ev.END_DATE_TIME - timedelta(hours=2)
        end = self.ev.END_DATE_TIME - timedelta(hours=1)
        self.assertFalse(self.prsn.is_available(st, end, self.tech))

    def test_if_busy(self):
        start = (Event.objects.get(SLUG="GDQ2").START_DATE_TIME
                 + timedelta(hours=1, minutes=30))
        end = (Event.objects.get(SLUG="GDQ2").START_DATE_TIME
               + timedelta(hours=2, minutes=30))
        self.assertTrue(self.prsn.is_busy(start, end))

    def test_if_not_busy(self):
        start = (Event.objects.get(SLUG="GDQ2").START_DATE_TIME
                 + timedelta(hours=2, minutes=30))
        end = (Event.objects.get(NAME="GDQ2").START_DATE_TIME
               + timedelta(minutes=30))
        self.assertFalse(self.prsn.is_busy(start, end))


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
        person = Person.objects.create(NICKNAME="Duncan")
        person.ROLES.set([role])
        avail_start = event_start_date + timedelta(minutes=30)
        avail_end = event_start_date + timedelta(hours=2)
        self.avail1 = AvailabilityBlock.objects.create(
                                                PERSON=person,
                                                EVENT=esaa,
                                                START_DATE_TIME=avail_start,
                                                END_DATE_TIME=avail_end)

    def test_avail_block_str(self):
        self.assertEqual(str(self.avail1),
                         f"{self.avail1.PERSON} @ "
                         + f"{self.avail1.START_DATE_TIME} "
                         + f"({self.avail1.EVENT})")


class RoleTestCase(TestCase):

    def setUp(self):
        event_start_date = datetime(year=2020, month=4, day=7, hour=11,
                                    tzinfo=timezone.utc)
        event_end_date = event_start_date + timedelta(days=1)
        self.gtam = Event.create(NAME="GTAMarathon 2027",
                                 SLUG="GTAM27",
                                 START_DATE_TIME=event_start_date,
                                 END_DATE_TIME=event_end_date)
        self.gtam.save()
        self.tech = Role.objects.create(NAME="Tech", EVENT=self.gtam)
        self.fund = Role.objects.create(NAME="Fundraising", EVENT=self.gtam)

    def test_role_default_margin(self):
        self.assertEqual(self.tech.TIME_SAFETY_MARGIN, timedelta(minutes=15))

    def test_role_str(self):
        self.assertEqual(str(self.tech), f"Tech ({self.gtam})")
