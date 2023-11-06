from django.test import TestCase
from django.contrib.auth.models import Group, User
from django.test import Client
from datetime import datetime, timedelta
from django.utils import timezone
from schedule.models import Event


class TestUploadCSV(TestCase):
    pass


class TestAddEvent(TestCase):
    pass


class TestEvent(TestCase):

    def setUp(self):
        staff_user = User.objects.create_user("notsosuper", "", "mypassword")
        User.objects.create_user("regularjoe", "", "password123")

        start = datetime(year=2018, month=6, day=21, hour=11,
                         tzinfo=timezone.utc)
        end = start + timedelta(days=1)
        ev = Event.create(NAME="GTAMarathon 2027",
                          SLUG="GTAM27",
                          START_DATE_TIME=start,
                          END_DATE_TIME=end)
        ev.save()
        staff_user.groups.add(ev.STAFF)

        self.staff_c = Client()
        self.staff_c.login(username="notsosuper", password="mypassword")
        self.non_staff_c = Client()
        self.non_staff_c.login(username="regularjoe", password="password123")

    def test_event_200(self):
        response = self.staff_c.get("/event/GTAM27/")
        self.assertEqual(response.status_code, 200)

    def test_event_template(self):
        response = self.staff_c.get("/event/GTAM27/")
        self.assertIn("schedule/base_event.html",
                      [x.name for x in response.templates])

    def test_event_doesnt_exit(self):
        response = self.staff_c.get("/event/GDQ29/")
        self.assertEqual(response.status_code, 404)

    def test_event_user_not_staff(self):
        response = self.non_staff_c.get("/event/GTAM27/")
        self.assertEqual(response.status_code, 403)

    def test_event_non_get_request(self):
        response = self.staff_c.post("/event/GTAM27/")
        self.assertEqual(response.status_code, 400)


class TestEditEvent(TestCase):

    def setUp(self):
        staff_user = User.objects.create_user("notsosuper", "", "mypassword")
        User.objects.create_user("regularjoe", "", "password123")

        start = datetime(year=2018, month=6, day=21, hour=11,
                         tzinfo=timezone.utc)
        end = start + timedelta(days=1)
        ev = Event.create(NAME="GTAMarathon 2027",
                          SLUG="GTAM27",
                          START_DATE_TIME=start,
                          END_DATE_TIME=end)
        ev.save()
        staff_user.groups.add(ev.STAFF)

        self.staff_c = Client()
        self.staff_c.login(username="notsosuper", password="mypassword")
        self.non_staff_c = Client()
        self.non_staff_c.login(username="regularjoe", password="password123")

    def test_edit_event_get_200(self):
        response = self.staff_c.get("/edit_event/GTAM27/")
        self.assertEqual(response.status_code, 200)

    def test_edit_event_get_non_existent_event(self):
        response = self.staff_c.get("/edit_event/yesimsure/")
        self.assertEqual(response.status_code, 404)

    def test_edit_event_get_not_staff(self):
        response = self.non_staff_c.get("/edit_event/GTAM27/")
        self.assertEqual(response.status_code, 403)

    def test_edit_event_get_template(self):
        response = self.staff_c.get("/edit_event/GTAM27/")
        self.assertIn("schedule/base_edit_event.html",
                      [x.name for x in response.templates])

    def test_edit_event_post_valid_effect(self):
        ev = Event.objects.get(SLUG="GTAM27")
        self.staff_c.post("/edit_event/GTAM27/",
                          {"NAME": "GTAMarathon 2027_2", "SLUG": ev.SLUG,
                           "START_DATE_TIME": ev.START_DATE_TIME,
                           "END_DATE_TIME": ev.END_DATE_TIME})
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
        response = self.staff_c.post("/edit_event/yesimsure/")
        self.assertEqual(response.status_code, 404)

    def test_edit_event_post_not_staff(self):
        ev = Event.objects.get(SLUG="GTAM27")
        response = self.non_staff_c.post(
                    "/edit_event/GTAM27/",
                    {"NAME": "GTAMarathon 2027_2",
                     "SLUG": ev.SLUG,
                     "START_DATE_TIME": ev.START_DATE_TIME,
                     "END_DATE_TIME": ev.END_DATE_TIME})
        self.assertEqual(response.status_code, 403)

    def test_edit_event_post_invalid(self):
        ev = Event.objects.get(SLUG="GTAM27")
        response = self.staff_c.post("/edit_event/GTAM27/",
                                     {"NAME": ev.NAME,
                                      "SLUG": ev.SLUG,
                                      "START_DATE_TIME": "yes I would",
                                      "END_DATE_TIME": ev.END_DATE_TIME})
        self.assertEqual(response.status_code, 400)
