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
        user = User.objects.create_user("notsosuper", "", "mypassword")
        start = datetime(year=2018, month=6, day=21, hour=11,
                         tzinfo=timezone.utc)
        end = start + timedelta(days=1)
        ev = Event.create(NAME="GTAMarathon 2027",
                          SLUG="GTAM27",
                          START_DATE_TIME=start,
                          END_DATE_TIME=end)
        ev.save()
        user.groups.add(ev.STAFF)
        self.c = Client()
        self.c.login(username="notsosuper", password="mypassword")

    def test_event_200(self):
        response = self.c.get("/event/GTAM27/")
        self.assertEqual(response.status_code, 200)
