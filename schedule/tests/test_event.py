from django.test import TestCase
from django.utils import timezone
from datetime import timedelta
from django.contrib.auth.models import Group, User
from django.test import Client


class EventTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create_user("notverysuper", "", "password1")
        c = Client()
        start_date = timezone.now()
        end_date = timezone.now() + timedelta(days=1)
        c.login(username="notverysuper", password="password1")
        c.post("/add_event/", {"NAME": "GSPS 2026", "SLUG": "GSPS26",
                               "START_DATE_TIME": start_date,
                               "END_DATE_TIME": end_date})

    def test_proper_group_was_made(self):
        self.assertTrue(Group.objects.filter(name="GSPS26 Staff"))
