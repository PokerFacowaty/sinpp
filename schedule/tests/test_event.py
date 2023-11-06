from django.test import TestCase
from django.utils import timezone
from datetime import timedelta, datetime
from django.contrib.auth.models import Group, User
from schedule.models import Event


class EventTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create_user("notverysuper", "", "password1")
        start_date = datetime(year=2020, month=4, day=7, hour=11,
                              tzinfo=timezone.utc)
        end_date = start_date + timedelta(days=1)
        Event.create(NAME="GSPS 2026", SLUG="GSPS26",
                     START_DATE_TIME=start_date, END_DATE_TIME=end_date)

    def test_proper_group_was_made(self):
        self.assertTrue(Group.objects.filter(name="GSPS26 Staff"))
