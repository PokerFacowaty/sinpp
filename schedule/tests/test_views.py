from django.test import TestCase, Client, RequestFactory
from django.contrib.auth.models import Group, User
from datetime import datetime, timedelta
from django.utils import timezone
from schedule.models import Event
from schedule.views import add_event, event, edit_event

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
        response = add_event(request)
        self.assertTrue(response.status_code, 200)

    def test_add_event_user_is_staff_member(self):
        self.c.post("/add_event/", {"NAME": "GSPS 2026", "SLUG": "GSPS26",
                                    "START_DATE_TIME": self.start,
                                    "END_DATE_TIME": self.end})
        self.assertTrue(self.user.groups.filter(name="GSPS26 Staff").exists())


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
