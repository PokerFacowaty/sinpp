from django.test import TestCase, Client, RequestFactory
from sinpp.views import user_profile, register_account
from django.contrib.auth.models import User
from schedule.models import Event, Room, Role
from datetime import datetime
from django.utils import timezone


class TestUserProfile(TestCase):

    def setUp(self):
        self.usr = User.objects.create_user("somedude", "", "somerduder")

        self.ev = Event.create(NAME="Movies Watched At Normal Speed",
                               SLUG="MWaNS",
                               START_DATE_TIME=datetime(year=2022, month=2,
                                                        day=3, hour=12,
                                                        tzinfo=timezone.utc),
                               END_DATE_TIME=datetime(year=2022, month=2,
                                                      day=3, hour=13,
                                                      tzinfo=timezone.utc))
        self.ev.save()
        self.usr.groups.add(self.ev.STAFF)

        self.rm = Room.objects.create(NAME="Stream 1", EVENT=self.ev)

        self.rl = Role.objects.create(NAME="Fundraising", EVENT=self.ev)

        self.c = Client()
        self.c.login(username="somedude", password="somerduder")

        self.factory = RequestFactory()

    def test_user_profile_template(self):
        response = self.c.get("/accounts/profile/")
        self.assertIn("registration/profile.html",
                      [x.name for x in response.templates])

    def test_user_profile_roles(self):
        response = self.c.get("/accounts/profile/")
        self.assertIn(self.rl, response.context["events"][0].roles)

    def test_user_profile_staff(self):
        response = self.c.get("/accounts/profile/")
        self.assertIn(self.usr, response.context["events"][0].staff)

    def test_user_profile_rooms(self):
        response = self.c.get("/accounts/profile/")
        self.assertIn(self.rm, response.context["events"][0].rooms)

    def test_user_profile_non_get(self):
        request = self.factory.post("/accounts/profile/")
        request.user = self.usr
        response = user_profile(request)
        self.assertEqual(response.status_code, 400)


class TestRegisterAccount(TestCase):

    def setUp(self):
        self.c = Client()
        self.factory = RequestFactory()

    def test_register_post_effect(self):
        request = self.factory.post("/accounts/register/",
                                    {"username": "myusername",
                                     "password1": "3tcF9sf@y@@gHM5@HxuA",
                                     "password2": "3tcF9sf@y@@gHM5@HxuA"})
        register_account(request)
        self.assertTrue(User.objects.all())

    def test_register_post_invalid_form(self):
        request = self.factory.post("/accounts/register/",
                                    {"username": "myusername",
                                     "password1": "123",
                                     "password2": "123"})
        response = register_account(request)
        self.assertEqual(response.status_code, 400)
