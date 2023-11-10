from django.test import TestCase, Client, RequestFactory
from django.contrib.auth.models import Group, User
from datetime import datetime, timedelta
from django.utils import timezone
from schedule.models import Event, Role, Speedrun, Room, Intermission, Shift
from schedule.views import (add_event, event, edit_event, remove_event,
                            add_role, role, edit_role, remove_role,
                            room_schedule, add_shift, shift, edit_shift,
                            remove_shift, add_staff, remove_staff)
import math
from django.http import Http404, JsonResponse
from django.core import serializers

'''I am using a RequestFactory for whenever I don't need the additional
   functions the Client provides (such as checking for templates used) and
   a Client whenever I do.'''


class TestUploadCSV(TestCase):
    pass


class TestAddEvent(TestCase):
    def setUp(self):
        self.user = User.objects.create_user("notverysuper", "", "password1")
        self.c = Client()

        self.start = datetime(year=2020, month=4, day=7, hour=11,
                              tzinfo=timezone.utc)
        self.end = self.start + timedelta(days=1)

        self.c.login(username="notverysuper", password="password1")

        self.factory = RequestFactory()

    def test_add_event_post_valid(self):
        request = self.factory.post("/add_event/",
                                    {"NAME": "GSPS 2026",
                                     "SLUG": "GSPS26",
                                     "START_DATE_TIME": self.start,
                                     "END_DATE_TIME": self.end})
        request.user = self.user
        add_event(request)
        ev = Event.objects.filter(SLUG="GSPS26")
        self.assertTrue(ev)

    def test_add_event_post_invalid(self):
        request = self.factory.post("/add_event/",
                                    {"NAME": "GSPS 2026",
                                     "SLUG": "GSPS26",
                                     "START_DATE_TIME": "yesitdoes",
                                     "END_DATE_TIME": self.end})
        request.user = self.user
        response = add_event(request)
        self.assertEqual(response.status_code, 400)

    def test_add_event_post_valid_redirect(self):
        response = self.c.post("/add_event/",
                               {"NAME": "GSPS 2026",
                                "SLUG": "GSPS26",
                                "START_DATE_TIME": self.start,
                                "END_DATE_TIME": self.end}, follow=True)
        self.assertEqual(response.resolver_match.url_name, "user_profile")

    def test_add_event_not_get_or_post(self):
        request = self.factory.delete("/add_event/",
                                      {"NAME": "GSPS 2026",
                                       "SLUG": "GSPS26",
                                       "START_DATE_TIME": self.start,
                                       "END_DATE_TIME": self.end})
        request.user = self.user
        response = add_event(request)
        self.assertEqual(response.status_code, 400)

    def test_add_event_staff_group_exists(self):
        self.c.post("/add_event/", {"NAME": "GSPS 2026", "SLUG": "GSPS26",
                                    "START_DATE_TIME": self.start,
                                    "END_DATE_TIME": self.end})
        self.assertTrue(Group.objects.filter(name="GSPS26 Staff"))

    def test_add_event_user_is_staff_member(self):
        self.c.post("/add_event/", {"NAME": "GSPS 2026", "SLUG": "GSPS26",
                                    "START_DATE_TIME": self.start,
                                    "END_DATE_TIME": self.end})
        self.assertTrue(self.user.groups.filter(name="GSPS26 Staff").exists())

    def test_add_event_get_200(self):
        request = self.factory.get("/add_event/")
        request.user = self.user
        response = add_event(request)
        self.assertEqual(response.status_code, 200)

    def test_add_event_get_template(self):
        response = self.c.get("/add_event/")
        self.assertIn("schedule/base_add_event.html",
                      [x.name for x in response.templates])


class TestEvent(TestCase):

    def setUp(self):
        self.staff_user = User.objects.create_user("notsosuper",
                                                   "", "mypassword")
        self.non_staff_user = User.objects.create_user("regularjoe",
                                                       "", "password123")

        start = datetime(year=2018, month=6, day=21, hour=11,
                         tzinfo=timezone.utc)
        end = start + timedelta(days=1)
        ev = Event.create(NAME="GTAMarathon 2027",
                          SLUG="GTAM27",
                          START_DATE_TIME=start,
                          END_DATE_TIME=end)
        ev.save()
        self.staff_user.groups.add(ev.STAFF)

        self.staff_c = Client()
        self.staff_c.login(username="notsosuper", password="mypassword")
        self.non_staff_c = Client()
        self.non_staff_c.login(username="regularjoe", password="password123")

        self.factory = RequestFactory()

    def test_event_200(self):
        request = self.factory.get("/event/GTAM27/")
        request.user = self.staff_user
        response = event(request, "GTAM27")
        self.assertEqual(response.status_code, 200)

    def test_event_template(self):
        response = self.staff_c.get("/event/GTAM27/")
        self.assertIn("schedule/base_event.html",
                      [x.name for x in response.templates])

    def test_event_doesnt_exit(self):
        request = self.factory.get("/event/GDQ29/")
        request.user = self.staff_user
        response = event(request, "GDQ29")
        self.assertEqual(response.status_code, 404)

    def test_event_user_not_staff(self):
        request = self.factory.get("/event/GTAM27/")
        request.user = self.non_staff_user
        response = event(request, "GTAM27")
        self.assertEqual(response.status_code, 403)

    def test_event_non_get_request(self):
        request = self.factory.post("/event/GTAM27/")
        request.user = self.staff_user
        response = event(request, "GTAM27")
        self.assertEqual(response.status_code, 400)


class TestEditEvent(TestCase):

    def setUp(self):
        self.staff_user = User.objects.create_user("notsosuper",
                                                   "", "mypassword")
        self.non_staff_user = User.objects.create_user("regularjoe",
                                                       "", "password123")

        start = datetime(year=2018, month=6, day=21, hour=11,
                         tzinfo=timezone.utc)
        end = start + timedelta(days=1)
        ev = Event.create(NAME="GTAMarathon 2027",
                          SLUG="GTAM27",
                          START_DATE_TIME=start,
                          END_DATE_TIME=end)
        ev.save()
        self.staff_user.groups.add(ev.STAFF)

        self.staff_c = Client()
        self.staff_c.login(username="notsosuper", password="mypassword")
        self.non_staff_c = Client()
        self.non_staff_c.login(username="regularjoe", password="password123")

        self.factory = RequestFactory()

    def test_edit_event_get_200(self):
        request = self.factory.get("/edit_event/GTAM27/")
        request.user = self.staff_user
        response = edit_event(request, "GTAM27")
        self.assertEqual(response.status_code, 200)

    def test_edit_event_get_non_existent_event(self):
        request = self.factory.get("/edit_event/yesimsure/")
        request.user = self.staff_user
        response = edit_event(request, "yesimsure")
        self.assertEqual(response.status_code, 404)

    def test_edit_event_get_not_staff(self):
        request = self.factory.get("/edit_event/GTAM27/")
        request.user = self.non_staff_user
        response = edit_event(request, "GTAM27")
        self.assertEqual(response.status_code, 403)

    def test_edit_event_get_template(self):
        response = self.staff_c.get("/edit_event/GTAM27/")
        self.assertIn("schedule/base_edit_event.html",
                      [x.name for x in response.templates])

    def test_edit_event_post_valid_effect(self):
        ev = Event.objects.get(SLUG="GTAM27")
        request = self.factory.post("/edit/event/GTAM27/",
                                    {"NAME": "GTAMarathon 2027_2",
                                     "SLUG": ev.SLUG,
                                     "START_DATE_TIME": ev.START_DATE_TIME,
                                     "END_DATE_TIME": ev.END_DATE_TIME})
        request.user = self.staff_user
        edit_event(request, "GTAM27")
        ev = Event.objects.get(SLUG="GTAM27")
        self.assertEqual(ev.NAME, "GTAMarathon 2027_2")

    def test_edit_event_post_valid_redirect(self):
        ev = Event.objects.get(SLUG="GTAM27")
        response = self.staff_c.post("/edit_event/GTAM27/",
                                     {"NAME": "GTAMarathon 2027_2",
                                      "SLUG": ev.SLUG,
                                      "START_DATE_TIME": ev.START_DATE_TIME,
                                      "END_DATE_TIME": ev.END_DATE_TIME},
                                     follow=True)
        self.assertEqual(response.resolver_match.url_name, "event")

    def test_edit_event_post_non_existent_event(self):
        request = self.factory.post("/edit_event/yesimsure/")
        request.user = self.staff_user
        response = edit_event(request, "yesimsure")
        self.assertEqual(response.status_code, 404)

    def test_edit_event_post_not_staff(self):
        ev = Event.objects.get(SLUG="GTAM27")
        request = self.factory.post(
                    "/edit_event/GTAM27/",
                    {"NAME": "GTAMarathon 2027_2",
                     "SLUG": ev.SLUG,
                     "START_DATE_TIME": ev.START_DATE_TIME,
                     "END_DATE_TIME": ev.END_DATE_TIME})
        request.user = self.non_staff_user
        response = edit_event(request, "GTAM27")
        self.assertEqual(response.status_code, 403)

    def test_edit_event_post_invalid(self):
        ev = Event.objects.get(SLUG="GTAM27")
        request = self.factory.post("/edit_event/GTAM27/",
                                    {"NAME": ev.NAME,
                                     "SLUG": ev.SLUG,
                                     "START_DATE_TIME": "yes I would",
                                     "END_DATE_TIME": ev.END_DATE_TIME})
        request.user = self.staff_user
        response = edit_event(request, "GTAM27")
        self.assertEqual(response.status_code, 400)

    def test_edit_event_unaccepted_request(self):
        request = self.factory.delete("/edit_event/GTAM27/")
        request.user = self.staff_user
        response = edit_event(request, "GTAM27")
        self.assertEqual(response.status_code, 400)


class TestRemoveEvent(TestCase):

    def setUp(self):
        self.staff_user = User.objects.create_user("userandstuff",
                                                   "", "123456")
        self.non_staff = User.objects.create_user("nostaffhere",
                                                  "", "123456789")

        start = datetime(year=2005, month=4, day=16, hour=9,
                         tzinfo=timezone.utc)
        end = start + timedelta(days=2)
        ev = Event.create(NAME="Games Done Moderately Fast '96",
                          SLUG="GDMF96",
                          START_DATE_TIME=start,
                          END_DATE_TIME=end)
        ev.save()
        self.staff_user.groups.add(ev.STAFF)

        self.c = Client()
        self.c.login(username="userandstuff", password="123456")

        self.factory = RequestFactory()

    def test_remove_event_get_200(self):
        request = self.factory.get("/remove_event/GDMF96")
        request.user = self.staff_user
        response = remove_event(request, "GDMF96")
        self.assertEqual(response.status_code, 200)

    def test_remove_event_get_non_existent_event(self):
        request = self.factory.get("/remove_event/someventiguess")
        request.user = self.staff_user
        response = remove_event(request, "someeventiguess")
        self.assertEqual(response.status_code, 404)

    def test_remove_event_get_non_staff_user(self):
        request = self.factory.get("/remove_event/GDMF96")
        request.user = self.non_staff
        response = remove_event(request, "GDMF96")
        self.assertEqual(response.status_code, 403)

    def test_remove_event_get_template(self):
        response = self.c.get("/remove_event/GDMF96/")
        self.assertIn("schedule/base_remove_event.html",
                      [x.name for x in response.templates])

    def test_remove_event_not_get_or_post(self):
        request = self.factory.delete("/remove_event/GDMF96")
        request.user = self.staff_user
        response = remove_event(request, "GDMF96")
        self.assertEqual(response.status_code, 400)

    def test_remove_event_post_effect(self):
        request = self.factory.post("/remove_event/GDMF96")
        request.user = self.staff_user
        remove_event(request, "GDMF96")
        self.assertFalse(Event.objects.filter(SLUG="GDMF96"))

    def test_remove_event_post_non_existent_event(self):
        request = self.factory.post("/remove_event/someeventiguess")
        request.user = self.staff_user
        response = remove_event(request, "someeventiguess")
        self.assertEqual(response.status_code, 404)

    def test_remove_event_post_redirect(self):
        response = self.c.post("/remove_event/GDMF96/", follow=True)
        self.assertEqual(response.resolver_match.url_name, "user_profile")

    def test_remove_event_post_non_staff_user(self):
        request = self.factory.post("/remove_event/GDMF96/")
        request.user = self.non_staff
        response = remove_event(request, "GDMF96")
        self.assertEqual(response.status_code, 403)


class TestAddRole(TestCase):

    def setUp(self):
        self.staff_user = User.objects.create_user("IusethereforeIam",
                                                   "", "qwerty")
        self.non_staff_user = User.objects.create_user("nostaffforme",
                                                       "", "qwertyuiop")

        start = datetime(year=2011, month=3, day=1, hour=11,
                         tzinfo=timezone.utc)
        end = start + timedelta(days=3)
        self.ev = Event.create(NAME="Religious Mothers Against Speedrunning 4",
                               SLUG="RMAS4",
                               START_DATE_TIME=start,
                               END_DATE_TIME=end)
        self.ev.save()

        self.staff_user.groups.add(self.ev.STAFF)

        self.c = Client()
        self.c.login(username="IusethereforeIam", password="qwerty")

        self.factory = RequestFactory()

    def test_add_role_post_effect(self):
        request = self.factory.post("/add_role/RMAS4",
                                    {"NAME": "Fundraising",
                                     "EVENT": self.ev,
                                     "TIME_SAFETY_MARGIN": "00:15:00"})
        request.user = self.staff_user
        add_role(request, "RMAS4")
        self.assertTrue(Role.objects.filter(NAME="Fundraising", EVENT=self.ev))

    def test_add_role_post_redirect(self):
        response = self.c.post("/add_role/RMAS4/",
                               {"NAME": "Fundraising",
                                "EVENT": self.ev,
                                "TIME_SAFETY_MARGIN": "00:15:00"},
                               follow=True)
        self.assertEqual(response.resolver_match.url_name, "event")

    def test_add_role_post_invalid(self):
        request = self.factory.post("/add_role/RMAS4/",
                                    {"NAME": "Fundraising",
                                     "EVENT": self.ev,
                                     "TIME_SAFETY_MARGIN": "idlikeoneyeah"},
                                    follow=True)
        request.user = self.staff_user
        response = add_role(request, "RMAS4")
        self.assertEqual(response.status_code, 400)

    def test_add_role_post_not_get_or_post(self):
        request = self.factory.delete("/add_role/RMAS4/")
        request.user = self.staff_user
        response = add_role(request, "RMAS4")
        self.assertEqual(response.status_code, 400)

    def test_add_role_post_non_staff_user(self):
        request = self.factory.post("/add_role/RMAS4/",
                                    {"NAME": "Fundraising",
                                     "EVENT": self.ev,
                                     "TIME_SAFETY_MARGIN": "00:15:00"},
                                    follow=True)
        request.user = self.non_staff_user
        response = add_role(request, "RMAS4")
        self.assertEqual(response.status_code, 403)

    def test_add_role_post_nonexistent_event(self):
        request = self.factory.post("/add_role/FathersWhoSpeedrun/",
                                    {"NAME": "Fundraising",
                                     "EVENT": self.ev,
                                     "TIME_SAFETY_MARGIN": "00:15:00"},
                                    follow=True)
        request.user = self.staff_user
        response = add_role(request, "FathersWhoSpeedrun")
        self.assertEqual(response.status_code, 404)

    def test_add_role_get_template(self):
        response = self.c.get("/add_role/RMAS4/")
        self.assertIn("schedule/base_add_role.html",
                      [x.name for x in response.templates])

    def test_add_role_get_non_staff_user(self):
        request = self.factory.get("/add_role/RMAS4/")
        request.user = self.non_staff_user
        response = add_role(request, "RMAS4")
        self.assertEqual(response.status_code, 403)

    def test_add_role_get_nonexistent_event(self):
        request = self.factory.get("/add_role/FathersWhoSpeedrun/")
        request.user = self.staff_user
        response = add_role(request, "FathersWhoSpeedrun")
        self.assertEqual(response.status_code, 404)


class TestRole(TestCase):

    def setUp(self):
        self.staff_user = User.objects.create_user("StanleyIs",
                                                   "", "CheatingOnHisWife")
        self.non_staff = User.objects.create_user("HowDoYouUntellSomething",
                                                  "", "YouCant")

        start = datetime(year=2003, month=7, day=12, hour=10,
                         tzinfo=timezone.utc)
        end = start + timedelta(days=2)
        self.ev = Event.create(NAME="A Baby Conceived Out Of Wedlock",
                               SLUG="BCOOW",
                               START_DATE_TIME=start,
                               END_DATE_TIME=end)
        self.ev.save()

        self.staff_user.groups.add(self.ev.STAFF)

        self.rl = Role.objects.create(NAME="One True Rumour", EVENT=self.ev)
        self.rl.save()

        self.c = Client()
        self.c.login(username="StanleyIs", password="CheatingOnHisWife")

        self.factory = RequestFactory()

    def test_role_get_template(self):
        response = self.c.get(f"/role/{self.rl.id}/")
        self.assertIn("schedule/base_role.html",
                      [x.name for x in response.templates])

    def test_role_not_get(self):
        request = self.factory.delete(f"/role/{self.rl.id}/")
        request.user = self.staff_user
        response = role(request, self.rl.id)
        self.assertEqual(response.status_code, 400)

    def test_role_non_staff_user(self):
        request = self.factory.get(f"/role/{self.rl.id}/")
        request.user = self.non_staff
        response = role(request, self.rl.id)
        self.assertEqual(response.status_code, 403)

    def test_role_non_existent_role(self):
        request = self.factory.get("/role/123456/")
        request.user = self.staff_user
        response = role(request, 123456)
        self.assertEqual(response.status_code, 404)


class TestEditRole(TestCase):

    def setUp(self):
        self.staff_user = User.objects.create_user("Mocking Ridiculing",
                                                   "", "Dork Game")
        self.non_staff = User.objects.create_user("Could you have picked",
                                                  "", "tom bring on a plane")

        start = datetime(year=2016, month=2, day=9, hour=12,
                         tzinfo=timezone.utc)
        end = start + timedelta(days=2)
        self.ev = Event.create(NAME="Healthy Relationship Now",
                               SLUG="HRN",
                               START_DATE_TIME=start,
                               END_DATE_TIME=end)
        self.ev.save()

        self.staff_user.groups.add(self.ev.STAFF)

        self.rl = Role.objects.create(NAME="Best wingman", EVENT=self.ev)
        self.rl.save()

        self.c = Client()
        self.c.login(username="Mocking Ridiculing", password="Dork Game")

        self.factory = RequestFactory()

    def test_edit_role_get_template(self):
        response = self.c.get(f"/edit_role/{self.rl.id}/")
        self.assertIn("schedule/base_edit_role.html",
                      [x.name for x in response.templates])

    def test_edit_role_get_non_staff_user(self):
        request = self.factory.get(f"/edit_role/{self.rl.id}/")
        request.user = self.non_staff
        response = edit_role(request, self.rl.id)
        self.assertEqual(response.status_code, 403)

    def test_edit_role_get_nonexistent_role(self):
        request = self.factory.get("/edit_role/123456/")
        request.user = self.staff_user
        response = edit_role(request, 123456)
        self.assertEqual(response.status_code, 404)

    def test_edit_role_not_get_or_post(self):
        request = self.factory.put(f"/edit_role/{self.rl.id}/")
        request.user = self.staff_user
        response = edit_role(request, self.rl.id)
        self.assertEqual(response.status_code, 400)

    def test_edit_role_post_effect(self):
        self.c.post(
            f"/edit_role/{self.rl.id}/",
            {"NAME": "The same but better",
             "EVENT": self.ev,
             "TIME_SAFETY_MARGIN": self.rl.TIME_SAFETY_MARGIN},
            follow=True)
        self.assertEqual(Role.objects.get(pk=self.rl.id).NAME,
                         "The same but better")

    def test_edit_role_post_redirect(self):
        response = self.c.post(
            f"/edit_role/{self.rl.id}/",
            {"NAME": self.rl.NAME,
             "EVENT": self.ev,
             "TIME_SAFETY_MARGIN": self.rl.TIME_SAFETY_MARGIN},
            follow=True)
        self.assertEqual(response.resolver_match.url_name, "role")

    def test_edit_role_post_invalid_form(self):
        request = self.factory.post(
            f"/edit_role/{self.rl.id}/",
            {"NAME": self.rl.NAME,
             "EVENT": self.ev,
             "TIME_SAFETY_MARGIN": "notfeelingstringyarewe"},
            follow=True)
        request.user = self.staff_user
        response = edit_role(request, self.rl.id)
        self.assertEqual(response.status_code, 400)

    def test_edit_role_post_non_staff_user(self):
        request = self.factory.post(f"/edit_role/{self.rl.id}/")
        request.user = self.non_staff
        response = edit_role(request, self.rl.id)
        self.assertEqual(response.status_code, 403)

    def test_edit_role_post_nonexistent_role(self):
        request = self.factory.post("/edit_role/123456/")
        request.user = self.staff_user
        response = edit_role(request, 123456)
        self.assertEqual(response.status_code, 404)


class TestRemoveRole(TestCase):

    def setUp(self):
        self.staff_user = User.objects.create_user("fristajla",
                                                   "", "łakamakafą")
        self.non_staff = User.objects.create_user("jesusimreallyrunningoutof",
                                                  "", "ideasits326am")

        start = datetime(year=2016, month=2, day=9, hour=12,
                         tzinfo=timezone.utc)
        end = start + timedelta(days=2)
        self.ev = Event.create(NAME="And I Can't Sleep On a Weekday",
                               SLUG="AICSOW",
                               START_DATE_TIME=start,
                               END_DATE_TIME=end)
        self.ev.save()

        self.staff_user.groups.add(self.ev.STAFF)

        self.rl = Role.objects.create(NAME="Best wingman", EVENT=self.ev)
        self.rl.save()

        self.c = Client()
        self.c.login(username="fristajla", password="łakamakafą")

        self.factory = RequestFactory()

    def test_remove_role_post_effect(self):
        request = self.factory.post(f"/remove_role/{self.rl.id}/")
        request.user = self.staff_user
        remove_role(request, self.rl.id)
        self.assertFalse(Role.objects.filter(pk=self.rl.id))

    def test_remove_role_post_non_staff_user(self):
        request = self.factory.post(f"/remove_role/{self.rl.id}/")
        request.user = self.non_staff
        response = remove_role(request, self.rl.id)
        self.assertEqual(response.status_code, 403)

    def test_remove_role_post_non_existent_role(self):
        request = self.factory.post("/remove_role/123456/")
        request.user = self.staff_user
        response = remove_role(request, 123456)
        self.assertEqual(response.status_code, 404)

    def test_remove_role_get_template(self):
        response = self.c.get(f"/remove_role/{self.rl.id}/")
        self.assertIn("schedule/base_remove_role.html",
                      [x.name for x in response.templates])

    def test_remove_role_get_non_staff_user(self):
        request = self.factory.get(f"/remove_role/{self.rl.id}/")
        request.user = self.non_staff
        response = remove_role(request, self.rl.id)
        self.assertEqual(response.status_code, 403)

    def test_remove_role_get_non_existent_role(self):
        request = self.factory.get("/remove_role/123456/")
        request.user = self.staff_user
        response = remove_role(request, 123456)
        self.assertEqual(response.status_code, 404)


class TestRoomSchedule(TestCase):

    def setUp(self):
        self.staff_user = User.objects.create_user("IOwnThisCity",
                                                   "", "OopsImeantevent")
        self.non_staff_user = User.objects.create_user("Bernard",
                                                       "Icantwaittogotojail")

        start = datetime(year=2005, month=4, day=16, hour=9,
                         tzinfo=timezone.utc)
        end = start + timedelta(days=1)
        self.ev = Event.create(NAME="Antarctic Speedrunner Assembly '05",
                               SLUG="ASA5",
                               START_DATE_TIME=start,
                               END_DATE_TIME=end)
        self.ev.save()

        self.rm = Room.objects.create(EVENT=self.ev,
                                      NAME="Stream 1",
                                      SLUG="S1")
        self.rm.save()

        sr1_st = self.ev.START_DATE_TIME
        sr1 = Speedrun.objects.create(EVENT=self.ev,
                                      ROOM=self.rm,
                                      GAME="Grand Theft Auto: Vice City",
                                      START_DATE_TIME=sr1_st,
                                      ESTIMATE=timedelta(hours=1))
        sr1.save()

        interm_st = sr1.END_DATE_TIME
        interm = Intermission.objects.create(EVENT=self.ev,
                                             ROOM=self.rm,
                                             START_DATE_TIME=interm_st,
                                             DURATION=timedelta(minutes=15))
        interm.save()

        sr2 = Speedrun.objects.create(EVENT=self.ev,
                                      ROOM=self.rm,
                                      GAME="Grand Theft Auto III",
                                      START_DATE_TIME=interm.END_DATE_TIME,
                                      ESTIMATE=timedelta(hours=3))

        fund = Role.objects.create(NAME="Fundraising", EVENT=self.ev)
        fund.save()
        tech = Role.objects.create(NAME="Tech", EVENT=self.ev)
        tech.save()

        Shift.objects.create(ROLE=fund,
                             EVENT=self.ev,
                             ROOM=self.rm,
                             START_DATE_TIME=sr1.START_DATE_TIME,
                             END_DATE_TIME=interm.END_DATE_TIME)
        Shift.objects.create(ROLE=fund,
                             EVENT=self.ev,
                             ROOM=self.rm,
                             START_DATE_TIME=interm.END_DATE_TIME,
                             END_DATE_TIME=sr2.END_DATE_TIME)
        Shift.objects.create(ROLE=tech,
                             EVENT=self.ev,
                             ROOM=self.rm,
                             START_DATE_TIME=self.ev.END_DATE_TIME,
                             END_DATE_TIME=sr2.END_DATE_TIME)

        self.staff_user.groups.add(self.ev.STAFF)

        self.c = Client()
        self.c.login(username="IOwnThisCity", password="OopsImeantevent")

        self.factory = RequestFactory()

    def test_room_schedule_template(self):
        response = self.c.get(f"/schedule/{self.ev.SLUG}/{self.rm.SLUG}/")
        self.assertIn("schedule/base_schedule.html",
                      [x.name for x in response.templates])

    def test_room_schedule_context_room(self):
        response = self.c.get(f"/schedule/{self.ev.SLUG}/{self.rm.SLUG}/")
        self.assertEqual(response.context["room"], self.rm)

    def test_room_schedule_context_runs_interms(self):
        response = self.c.get(f"/schedule/{self.ev.SLUG}/{self.rm.SLUG}/")
        runs = Speedrun.objects.filter(EVENT=self.ev, ROOM=self.rm)
        interms = Intermission.objects.filter(EVENT=self.ev, ROOM=self.rm)
        timed_runs = [{'type': 'run',
                       'obj': x,
                       'start_mins_rel': (
                            (x.START_DATE_TIME
                             - self.ev.START_DATE_TIME).total_seconds() // 60),
                       'length_mins_rel': math.ceil(
                            x.ESTIMATE.total_seconds() // 60
                        )} for x in runs]
        timed_interms = [{'type': 'interm',
                          'obj': x,
                          'start_mins_rel': (
                               (x.START_DATE_TIME
                                - self.ev.START_DATE_TIME).total_seconds()
                               // 60),
                          'length_mins_rel': math.ceil(
                               x.DURATION.total_seconds() // 60
                           )} for x in interms]
        runs_interms = [x for x in timed_runs]
        runs_interms.extend(timed_interms)
        runs_interms.sort(key=lambda x: x["obj"].START_DATE_TIME)
        self.maxDiff = None
        self.assertCountEqual(response.context["runs_interms"], runs_interms)

    def get_info_for_times(self):
        ev_start = self.ev.START_DATE_TIME
        ev_end = self.ev.END_DATE_TIME

        rounded_start = (ev_start
                         - timedelta(minutes=ev_start.minute,
                                     seconds=ev_start.second,
                                     microseconds=ev_start.microsecond))
        rounded_end = (ev_end + timedelta(hours=1)
                       - timedelta(minutes=ev_end.minute,
                                   seconds=ev_end.second,
                                   microseconds=ev_end.microsecond))

        return rounded_start, rounded_end

    def test_room_schedule_context_times_length(self):
        response = self.c.get(f"/schedule/{self.ev.SLUG}/{self.rm.SLUG}/")
        rounded_start, rounded_end = self.get_info_for_times()
        ev_len_hours = (rounded_end
                        - rounded_start).total_seconds() // 60 // 60
        self.assertEqual(len(response.context["times"]), ev_len_hours + 1)

    def test_room_schedule_context_times_start(self):
        response = self.c.get(f"/schedule/{self.ev.SLUG}/{self.rm.SLUG}/")
        rounded_start, rounded_end = self.get_info_for_times()
        self.assertEqual(response.context["times"][0],
                         rounded_start.isoformat(sep="\n").split("+")[0])

    def test_room_schedule_context_times_end(self):
        response = self.c.get(f"/schedule/{self.ev.SLUG}/{self.rm.SLUG}/")
        rounded_start, rounded_end = self.get_info_for_times()
        self.assertEqual(response.context["times"][-1],
                         rounded_end.isoformat(sep="\n").split("+")[0])

    def test_room_schedule_context_shifts(self):
        response = self.c.get(f"/schedule/{self.ev.SLUG}/{self.rm.SLUG}/")
        role_shifts = {x: [y for y in Shift.objects.filter(EVENT=self.ev,
                                                           ROOM=self.rm,
                                                           ROLE=x)]
                       for x in Role.objects.filter(EVENT=self.ev)}
        for rl in role_shifts.values():
            for sh in rl:
                sh.volunteer_names = sh.VOLUNTEERS.all()
                sh.start_mins_rel = ((
                    sh.START_DATE_TIME
                    - self.ev.START_DATE_TIME).total_seconds() // 60)
                sh.length_mins_rel = math.ceil(
                    (sh.END_DATE_TIME
                     - sh.START_DATE_TIME).total_seconds() // 60)
                sh.start_iso = sh.START_DATE_TIME.isoformat()
                sh.end_iso = sh.END_DATE_TIME.isoformat()

        self.assertCountEqual(response.context["shifts"], role_shifts)

    def test_room_schedule_context_table_start(self):
        response = self.c.get(f"/schedule/{self.ev.SLUG}/{self.rm.SLUG}/")
        rounded_start, rounded_end = self.get_info_for_times()
        self.assertEqual(response.context["table_start"],
                         rounded_start.isoformat())

    def test_room_schedule_context_table_end(self):
        response = self.c.get(f"/schedule/{self.ev.SLUG}/{self.rm.SLUG}/")
        rounded_start, rounded_end = self.get_info_for_times()
        self.assertEqual(response.context["table_end"],
                         rounded_end.isoformat())

    def test_room_schedule_non_staff_user(self):
        request = self.factory.get(f"/schedule/{self.ev.SLUG}/{self.rm.SLUG}/")
        request.user = self.non_staff_user
        response = room_schedule(request, self.ev.SLUG, self.rm.SLUG)
        self.assertEqual(response.status_code, 403)

    def test_room_schedule_non_get_request(self):
        request = self.factory.post(
            f"/schedule/{self.ev.SLUG}/{self.rm.SLUG}/")
        request.user = self.staff_user
        response = room_schedule(request, self.ev.SLUG, self.rm.SLUG)
        self.assertEqual(response.status_code, 400)

    def test_room_schedule_nonexistent_event(self):
        request = self.factory.get("/schedule/someevent/s1/")
        request.user = self.staff_user

        with self.assertRaises(Http404):
            room_schedule(request, "someevent", self.rm.SLUG)

    def test_room_schedule_nonexistent_room(self):
        request = self.factory.get(f"/schedule/{self.ev.SLUG}/bathroom/")
        request.user = self.staff_user

        with self.assertRaises(Http404):
            room_schedule(request, self.ev.SLUG, "bathroom")


class TestAddShift(TestCase):

    def setUp(self):
        self.staff_user = User.objects.create_user("WhoTheLuckyLady",
                                                   "", "PamsMom")
        self.non_staff_user = User.objects.create_user("NeverTellPam",
                                                       "OverDinner")

        start = datetime(year=2005, month=4, day=16, hour=9,
                         tzinfo=timezone.utc)
        end = start + timedelta(days=1)
        self.ev = Event.create(NAME="Antarctic Speedrunner Assembly '05",
                               SLUG="ASA5",
                               START_DATE_TIME=start,
                               END_DATE_TIME=end)
        self.ev.save()

        self.rm = Room.objects.create(EVENT=self.ev,
                                      NAME="Stream 1",
                                      SLUG="S1")
        self.rm.save()

        self.fund = Role.objects.create(NAME="Fundraising", EVENT=self.ev)
        self.fund.save()

        self.staff_user.groups.add(self.ev.STAFF)

        self.c = Client()
        self.c.login(username="WhoTheLuckyLady", password="PamsMom")

        self.factory = RequestFactory()

        self.start_time = datetime(year=2005, month=4, day=16, hour=10,
                                   tzinfo=timezone.utc)
        self.end_time = datetime(year=2005, month=4, day=16, hour=11,
                                 tzinfo=timezone.utc)

    def test_add_shift_ajax_post_effect(self):
        payload = {"ROLE": self.fund.id,
                   "ROOM": self.rm.id,
                   "EVENT": self.ev.id,
                   "START_DATE_TIME": self.start_time.isoformat(),
                   "END_DATE_TIME": self.end_time.isoformat()}
        request = self.factory.post("/add_shift/",
                                    data={"payload": payload},
                                    headers={"X-Requested-With":
                                             "XMLHttpRequest"},
                                    content_type="application/json")
        request.user = self.staff_user
        add_shift(request)
        self.assertTrue(Shift.objects.filter(ROLE=self.fund, EVENT=self.ev))

    def test_add_shift_non_ajax_post(self):
        payload = {"ROLE": self.fund.id,
                   "ROOM": self.rm.id,
                   "EVENT": self.ev.id,
                   "START_DATE_TIME": self.start_time.isoformat(),
                   "END_DATE_TIME": self.end_time.isoformat()}
        request = self.factory.post("/add_shift/",
                                    data={"payload": payload},
                                    content_type="application/json")
        request.user = self.staff_user
        response = add_shift(request)
        self.assertEqual(response.status_code, 400)

    def test_add_shift_ajax_non_post(self):
        payload = {"ROLE": self.fund.id,
                   "ROOM": self.rm.id,
                   "EVENT": self.ev.id,
                   "START_DATE_TIME": self.start_time.isoformat(),
                   "END_DATE_TIME": self.end_time.isoformat()}
        request = self.factory.delete("/add_shift/",
                                      data={"payload": payload},
                                      headers={"X-Requested-With":
                                               "XMLHttpRequest"},
                                      content_type="application/json")
        request.user = self.staff_user
        response = add_shift(request)
        self.assertEqual(response.status_code, 400)

    def test_add_shift_non_staff_user(self):
        payload = {"ROLE": self.fund.id,
                   "ROOM": self.rm.id,
                   "EVENT": self.ev.id,
                   "START_DATE_TIME": self.start_time.isoformat(),
                   "END_DATE_TIME": self.end_time.isoformat()}
        request = self.factory.post("/add_shift/",
                                    data={"payload": payload},
                                    headers={"X-Requested-With":
                                             "XMLHttpRequest"},
                                    content_type="application/json")
        request.user = self.non_staff_user
        response = add_shift(request)
        self.assertEqual(response.status_code, 403)

    def test_add_shift_nonexistent_event(self):
        payload = {"ROLE": self.fund.id,
                   "ROOM": self.rm.id,
                   "EVENT": 123456,
                   "START_DATE_TIME": self.start_time.isoformat(),
                   "END_DATE_TIME": self.end_time.isoformat()}
        request = self.factory.post("/add_shift/",
                                    data={"payload": payload},
                                    headers={"X-Requested-With":
                                             "XMLHttpRequest"},
                                    content_type="application/json")
        request.user = self.staff_user
        response = add_shift(request)
        self.assertEqual(response.status_code, 404)


class TestShift(TestCase):

    def setUp(self):

        self.staff_user = User.objects.create_user("DoingThings",
                                                   "", "BeforeYouDie")
        self.non_staff_user = User.objects.create_user("DoIReallyWannaGo",
                                                       "", "Snowboarding")

        start = datetime(year=2010, month=8, day=21, hour=10,
                         tzinfo=timezone.utc)
        end = start + timedelta(days=2)
        self.ev = Event.create(NAME="You Like Lame Things 2010",
                               SLUG="YLLM2010",
                               START_DATE_TIME=start,
                               END_DATE_TIME=end)
        self.ev.save()

        self.rm = Room.objects.create(EVENT=self.ev,
                                      NAME="Stream 7",
                                      SLUG="S7")
        self.rm.save()

        self.tech = Role.objects.create(NAME="Tech", EVENT=self.ev)
        self.tech.save()

        self.staff_user.groups.add(self.ev.STAFF)

        self.c = Client()
        self.c.login(username="DoingThings", password="BeforeYouDie")

        self.factory = RequestFactory()

        self.start_time = datetime(year=2010, month=8, day=21, hour=10,
                                   tzinfo=timezone.utc)
        self.end_time = datetime(year=2010, month=8, day=21, hour=10,
                                 tzinfo=timezone.utc)
        self.shift = Shift.objects.create(ROLE=self.tech,
                                          ROOM=self.rm,
                                          EVENT=self.ev,
                                          START_DATE_TIME=self.start_time,
                                          END_DATE_TIME=self.end_time)
        self.shift.save()

    def test_shift_response_content(self):
        response = self.c.get(f"/shift/{self.shift.id}/",
                              headers={"X-Requested-With":
                                       "XMLHttpRequest"},
                              content_type="application/json")
        data = serializers.serialize('json', [self.shift])
        expected_response = JsonResponse({'context': data[1:-1]})
        self.assertEqual(response.content, expected_response.content)

    def test_shift_ajax_non_get(self):
        request = self.factory.post(f"/shift/{self.shift.id}/",
                                    headers={"X-Requested-With":
                                             "XMLHttpRequest"},
                                    content_type="application/json")
        request.user = self.staff_user
        response = shift(request, self.shift.id)
        self.assertEqual(response.status_code, 400)

    def test_shift_non_ajax_get(self):
        request = self.factory.get(f"/shift/{self.shift.id}/",
                                   content_type="application/json")
        request.user = self.staff_user
        response = shift(request, self.shift.id)
        self.assertEqual(response.status_code, 400)

    def test_shift_non_staff_user(self):
        request = self.factory.get(f"/shift/{self.shift.id}/",
                                   headers={"X-Requested-With":
                                            "XMLHttpRequest"},
                                   content_type="application/json")
        request.user = self.non_staff_user
        response = shift(request, self.shift.id)
        self.assertEqual(response.status_code, 403)

    def test_shift_nonexistent_shift(self):
        request = self.factory.get("/shift/12223444/",
                                   headers={"X-Requested-With":
                                            "XMLHttpRequest"},
                                   content_type="application/json")
        request.user = self.non_staff_user
        response = shift(request, 12223444)
        self.assertEqual(response.status_code, 404)


class TestEditShift(TestCase):

    def setUp(self):

        self.staff_user = User.objects.create_user("IDoDeclare",
                                                   "", "MamaJuJuBooBoo")
        self.non_staff_user = User.objects.create_user("Recreation",
                                                       "", "OfTheCrimeScene")

        start = datetime(year=1997, month=2, day=1, hour=8,
                         tzinfo=timezone.utc)
        end = start + timedelta(days=3)
        self.ev = Event.create(NAME="We Fully Expect To Be Out Of Money",
                               SLUG="WFETBOOF",
                               START_DATE_TIME=start,
                               END_DATE_TIME=end)
        self.ev.save()

        self.rm = Room.objects.create(EVENT=self.ev,
                                      NAME="Stream 7",
                                      SLUG="S7")
        self.rm.save()

        self.tech = Role.objects.create(NAME="Tech", EVENT=self.ev)
        self.tech.save()

        self.staff_user.groups.add(self.ev.STAFF)

        self.c = Client()
        self.c.login(username="DoingThings", password="BeforeYouDie")

        self.factory = RequestFactory()

        self.start_time = datetime(year=1997, month=2, day=1, hour=8,
                                   tzinfo=timezone.utc)
        self.end_time = datetime(year=1997, month=2, day=1, hour=10,
                                 tzinfo=timezone.utc)
        self.sh = Shift.objects.create(ROLE=self.tech,
                                       ROOM=self.rm,
                                       EVENT=self.ev,
                                       START_DATE_TIME=self.start_time,
                                       END_DATE_TIME=self.end_time)
        self.sh.save()

    def test_edit_shift_effect(self):
        new_end = (self.sh.END_DATE_TIME + timedelta(hours=1)).isoformat()
        request = self.factory.put(f"/edit_shift/{self.sh.id}/",
                                   headers={"X-Requested-With":
                                            "XMLHttpRequest"},
                                   data={"payload":
                                         {"END_DATE_TIME": new_end}},
                                   content_type="application/json")
        request.user = self.staff_user
        edit_shift(request, self.sh.id)
        self.assertTrue(
            Shift.objects.get(pk=self.sh.id).END_DATE_TIME.isoformat()
            == new_end)

    def test_edit_shift_ajax_not_put(self):
        new_end = (self.sh.END_DATE_TIME + timedelta(hours=1)).isoformat()
        request = self.factory.post(f"/edit_shift/{self.sh.id}/",
                                    headers={"X-Requested-With":
                                             "XMLHttpRequest"},
                                    data={"payload":
                                          {"END_DATE_TIME": new_end}},
                                    content_type="application/json")
        request.user = self.staff_user
        response = edit_shift(request, self.sh.id)
        self.assertEqual(response.status_code, 400)

    def test_edit_shift_not_ajax_put(self):
        new_end = (self.sh.END_DATE_TIME + timedelta(hours=1)).isoformat()
        request = self.factory.put(f"/edit_shift/{self.sh.id}/",
                                   data={"payload":
                                         {"END_DATE_TIME": new_end}},
                                   content_type="application/json")
        request.user = self.staff_user
        response = edit_shift(request, self.sh.id)
        self.assertEqual(response.status_code, 400)

    def test_edit_shift_non_staff_user(self):
        new_end = (self.sh.END_DATE_TIME + timedelta(hours=1)).isoformat()
        request = self.factory.put(f"/edit_shift/{self.sh.id}/",
                                   headers={"X-Requested-With":
                                            "XMLHttpRequest"},
                                   data={"payload":
                                         {"END_DATE_TIME": new_end}},
                                   content_type="application/json")
        request.user = self.non_staff_user
        response = edit_shift(request, self.sh.id)
        self.assertEqual(response.status_code, 403)

    def test_edit_shift_nonexistent_shift(self):
        new_end = (self.sh.END_DATE_TIME + timedelta(hours=1)).isoformat()
        request = self.factory.put("/edit_shift/12321/",
                                   headers={"X-Requested-With":
                                            "XMLHttpRequest"},
                                   data={"payload":
                                         {"END_DATE_TIME": new_end}},
                                   content_type="application/json")
        request.user = self.staff_user
        response = edit_shift(request, 12321)
        self.assertEqual(response.status_code, 404)


class TestRemoveShift(TestCase):

    def setUp(self):

        self.staff_user = User.objects.create_user("TwoSantasInTheRoom",
                                                   "", "ThingsGetRuthless")
        self.non_staff_user = User.objects.create_user("ExcuseMe",
                                                       "", "NotAGun")

        start = datetime(year=2016, month=7, day=9, hour=12,
                         tzinfo=timezone.utc)
        end = start + timedelta(days=1)
        self.ev = Event.create(NAME="Buy Me Something Expensive",
                               SLUG="BMSE",
                               START_DATE_TIME=start,
                               END_DATE_TIME=end)
        self.ev.save()

        self.rm = Room.objects.create(EVENT=self.ev,
                                      NAME="Conference Room",
                                      SLUG="CR")
        self.rm.save()

        self.mark = Role.objects.create(NAME="Market", EVENT=self.ev)
        self.mark.save()

        self.staff_user.groups.add(self.ev.STAFF)

        self.c = Client()
        self.c.login(username="TwoSantasInTheRoom",
                     password="ThingsGetRuthless")

        self.factory = RequestFactory()

        self.start_time = datetime(year=2016, month=7, day=9, hour=12,
                                   tzinfo=timezone.utc)
        self.end_time = datetime(year=2016, month=7, day=9, hour=13,
                                 tzinfo=timezone.utc)
        self.sh = Shift.objects.create(ROLE=self.mark,
                                       ROOM=self.rm,
                                       EVENT=self.ev,
                                       START_DATE_TIME=self.start_time,
                                       END_DATE_TIME=self.end_time)
        self.sh.save()

    def test_remove_shift_effect(self):
        request = self.factory.delete(f"/remove_shift/{self.sh.id}/",
                                      headers={"X-Requested-With":
                                               "XMLHttpRequest"},
                                      content_type="application/json")
        request.user = self.staff_user
        remove_shift(request, self.sh.id)
        self.assertFalse(Shift.objects.filter(pk=self.sh.id))

    def test_remove_shift_ajax_not_delete(self):
        request = self.factory.post(f"/remove_shift/{self.sh.id}/",
                                    headers={"X-Requested-With":
                                             "XMLHttpRequest"},
                                    content_type="application/json")
        request.user = self.staff_user
        response = remove_shift(request, self.sh.id)
        self.assertEqual(response.status_code, 400)

    def test_remove_shift_not_ajax_delete(self):
        request = self.factory.delete(f"/remove_shift/{self.sh.id}/",
                                      content_type="application/json")
        request.user = self.staff_user
        response = remove_shift(request, self.sh.id)
        self.assertEqual(response.status_code, 400)

    def test_remove_shift_non_staff_user(self):
        request = self.factory.delete(f"/remove_shift/{self.sh.id}/",
                                      headers={"X-Requested-With":
                                               "XMLHttpRequest"},
                                      content_type="application/json")
        request.user = self.non_staff_user
        response = remove_shift(request, self.sh.id)
        self.assertEqual(response.status_code, 403)

    def test_remove_shift_nonexistent_shift(self):
        request = self.factory.delete("/remove_shift/2017/",
                                      headers={"X-Requested-With":
                                               "XMLHttpRequest"},
                                      content_type="application/json")
        request.user = self.non_staff_user
        response = remove_shift(request, 2017)
        self.assertEqual(response.status_code, 404)


class TestAddStaff(TestCase):

    def setUp(self):

        self.staff_user = User.objects.create_user("Sabre",
                                                   "", "GlorifiedFactChecker")
        self.staff_to_be = User.objects.create_user("HaveFunYouTwo",
                                                    "", "YesWeWill")

        start = datetime(year=2016, month=7, day=9, hour=12,
                         tzinfo=timezone.utc)
        end = start + timedelta(days=1)
        self.ev = Event.create(NAME="Buy Me Something Expensive",
                               SLUG="BMSE",
                               START_DATE_TIME=start,
                               END_DATE_TIME=end)
        self.ev.save()
        self.staff_user.groups.add(self.ev.STAFF)

        self.factory = RequestFactory()

    def test_add_staff_effect(self):
        request = self.factory.post(f"/add_staff/{self.ev.id}/",
                                    data={"payload":
                                          {"username": "HaveFunYouTwo"}},
                                    headers={"X-Requested-With":
                                             "XMLHttpRequest"},
                                    content_type="application/json")
        request.user = self.staff_user
        add_staff(request, self.ev.id)
        self.assertTrue(self.staff_to_be.groups.filter(
                                            name=self.ev.STAFF.name).exists())

    def test_add_staff_already_a_member(self):
        request = self.factory.post(f"/add_staff/{self.ev.id}/",
                                    data={"payload":
                                          {"username": "Sabre"}},
                                    headers={"X-Requested-With":
                                             "XMLHttpRequest"},
                                    content_type="application/json")
        request.user = self.staff_user
        response = add_staff(request, self.ev.id)
        self.assertEqual(response.status_code, 409)

    def test_add_staff_nonexistent_user(self):
        request = self.factory.post(f"/add_staff/{self.ev.id}/",
                                    data={"payload":
                                          {"username": "Printer"}},
                                    headers={"X-Requested-With":
                                             "XMLHttpRequest"},
                                    content_type="application/json")
        request.user = self.staff_user
        response = add_staff(request, self.ev.id)
        self.assertEqual(response.status_code, 404)

    def test_add_staff_ajax_not_post(self):
        request = self.factory.delete(f"/add_staff/{self.ev.id}/",
                                      data={"payload":
                                            {"username": "HaveFunYouTwo"}},
                                      headers={"X-Requested-With":
                                               "XMLHttpRequest"},
                                      content_type="application/json")
        request.user = self.staff_user
        response = add_staff(request, self.ev.id)
        self.assertEqual(response.status_code, 400)

    def test_add_staff_not_ajax_post(self):
        request = self.factory.post(f"/add_staff/{self.ev.id}/",
                                    data={"payload":
                                          {"username": "HaveFunYouTwo"}},
                                    content_type="application/json")
        request.user = self.staff_user
        response = add_staff(request, self.ev.id)
        self.assertEqual(response.status_code, 400)

    def test_add_staff_non_staff_user(self):
        request = self.factory.post(f"/add_staff/{self.ev.id}/",
                                    data={"payload":
                                          {"username": "HaveFunYouTwo"}},
                                    headers={"X-Requested-With":
                                             "XMLHttpRequest"},
                                    content_type="application/json")
        request.user = self.staff_to_be
        response = add_staff(request, self.ev.id)
        self.assertEqual(response.status_code, 403)

    def test_add_staff_nonexistent_event(self):
        request = self.factory.post("/add_staff/1222/",
                                    data={"payload":
                                          {"username": "HaveFunYouTwo"}},
                                    headers={"X-Requested-With":
                                             "XMLHttpRequest"},
                                    content_type="application/json")
        request.user = self.staff_user
        response = add_staff(request, 1222)
        self.assertEqual(response.status_code, 404)


class TestRemoveStaff(TestCase):

    def setUp(self):
        self.staff_user = User.objects.create_user("manager",
                                                   "", "salesman")
        self.staff_user2 = User.objects.create_user("betterManager",
                                                    "", "Manuel")
        self.non_staff = User.objects.create_user("According",
                                                  "", "toTheManual")

        start = datetime(year=2009, month=3, day=2, hour=10,
                         tzinfo=timezone.utc)
        end = start + timedelta(days=2)
        self.ev = Event.create(NAME="For So Many Reasons '09",
                               SLUG="FSMR09",
                               START_DATE_TIME=start,
                               END_DATE_TIME=end)
        self.ev.save()
        self.staff_user.groups.add(self.ev.STAFF)
        self.staff_user2.groups.add(self.ev.STAFF)

        self.factory = RequestFactory()

    def test_remove_staff_effect(self):
        request = self.factory.delete(f"/remove_staff/{self.ev.id}/",
                                      data={"payload":
                                            {"username": "betterManager"}},
                                      headers={"X-Requested-With":
                                               "XMLHttpRequest"},
                                      content_type="application/json")
        request.user = self.staff_user
        remove_staff(request, self.ev.id)
        self.assertFalse(self.staff_user2.groups.filter(
                                            name=self.ev.STAFF.name).exists())

    def test_remove_staff_not_member(self):
        request = self.factory.delete(f"/remove_staff/{self.ev.id}/",
                                      data={"payload":
                                            {"username": "According"}},
                                      headers={"X-Requested-With":
                                               "XMLHttpRequest"},
                                      content_type="application/json")
        request.user = self.staff_user
        response = remove_staff(request, self.ev.id)
        self.assertEqual(response.status_code, 409)

    def test_remove_staff_ajax_not_delete(self):
        request = self.factory.post(f"/remove_staff/{self.ev.id}/",
                                    data={"payload":
                                          {"username": "betterManager"}},
                                    headers={"X-Requested-With":
                                             "XMLHttpRequest"},
                                    content_type="application/json")
        request.user = self.staff_user
        response = remove_staff(request, self.ev.id)
        self.assertEqual(response.status_code, 400)

    def test_remove_staff_not_ajax_delete(self):
        request = self.factory.delete(f"/remove_staff/{self.ev.id}/",
                                      data={"payload":
                                            {"username": "betterManager"}},
                                      content_type="application/json")
        request.user = self.staff_user
        response = remove_staff(request, self.ev.id)
        self.assertEqual(response.status_code, 400)

    def test_remove_staff_non_staff_user_requesting(self):
        request = self.factory.delete(f"/remove_staff/{self.ev.id}/",
                                      data={"payload":
                                            {"username": "betterManager"}},
                                      headers={"X-Requested-With":
                                               "XMLHttpRequest"},
                                      content_type="application/json")
        request.user = self.non_staff
        response = remove_staff(request, self.ev.id)
        self.assertEqual(response.status_code, 403)
