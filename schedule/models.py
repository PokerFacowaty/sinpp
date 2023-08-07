from django.db import models
from datetime import timedelta, datetime


class Event(models.Model):

    NAME = models.CharField(max_length=100)
    SHORT_TITLE = models.CharField(max_length=25)
    START_DATE_TIME = models.DateTimeField()
    END_DATE_TIME = models.DateTimeField()
    # How many minutes are added to each block before considering someone
    # available, setting this to 0 means that if a person's availability
    # starts at 15:00 and an activity starts at the same time, they're
    # considered available. Setting this to 15 means they have to be available
    # since at least 14:45 to be considered available for the activity.
    TIME_SAFETY_MARGIN = models.DurationField(default=timedelta(minutes=15))


class Speedrun(models.Model):

    EVENT = models.ForeignKey(Event, on_delete=models.CASCADE)
    GAME = models.CharField(max_length=25)
    CATEGORY = models.CharField(max_length=25, blank=True)

    # any volunteers taking part as runners, commentators
    VOLUNTEERS_ENGAGED = models.ManyToManyField(
                                        "Person",
                                        related_name="SPEEDRUNS_ENGAGED_IN")

    VOLUNTEER_SHIFTS = models.ManyToManyField("Shift", blank=True)
    START_TIME = models.DateTimeField()
    ESTIMATE = models.DurationField()
    END_TIME = models.DateTimeField()

    def save(self, *args, **kwargs):
        if self.END_TIME is None and self.ESTIMATE is not None:
            self.END_TIME = self.START_TIME + self.ESTIMATE
        elif self.END_TIME is not None and self.ESTIMATE is None:
            self.ESTIMATE = self.END_TIME - self.START_TIME
        super(Speedrun, self).save(*args, **kwargs)


class Intermission(models.Model):

    EVENT = models.ForeignKey(Event, on_delete=models.CASCADE)
    VOLUNTEER_SHIFTS = models.ManyToManyField(
                       "Person", related_name="INTERMISSIONS_ENGAGED_IN")
    START_TIME = models.DateTimeField()
    DURATION = models.DurationField()
    END_TIME = models.DateTimeField()

    def save(self, *args, **kwargs):
        if self.END_TIME is None and self.DURATION is not None:
            self.END_TIME = self.START_TIME + self.DURATION
        elif self.END_TIME is not None and self.DURATION is None:
            self.DURATION = self.END_TIME - self.START_TIME


class Shift(models.Model):
    '''A single shift of one or more volunteers'''

    VOLUNTEER = models.ManyToManyField("Person")
    ROLE = models.ForeignKey("Role", on_delete=models.CASCADE)
    EVENT = models.ForeignKey("Event", on_delete=models.CASCADE)
    START_DATE_TIME = models.DateTimeField()
    END_DATE_TIME = models.DateTimeField()

    SPEEDRUNS = models.ManyToManyField("Speedrun", blank=True)


class Person(models.Model):
    NICKNAME = models.CharField(max_length=25)
    PRONOUNS = models.CharField(max_length=25, blank=True)
    # PROFILES = models.ManyToManyField(SocialMediaProfile)
    ROLES = models.ManyToManyField("Role", blank=True)

    def is_available(self, start_time: datetime, end_time: datetime,
                     event: Event) -> bool:
        blocks = AvailabilityBlock.objects.filter(PERSON=self)
        margin = event.TIME_SAFETY_MARGIN
        for bl in blocks:
            if ((start_time - bl.START_DATE_TIME) > margin
               and (bl.END_DATE_TIME - end_time) > margin):
                return True
        return False


class AvailabilityBlock(models.Model):
    PERSON = models.ForeignKey("Person", on_delete=models.CASCADE)
    EVENT = models.ForeignKey("Event", on_delete=models.CASCADE)
    START_DATE_TIME = models.DateTimeField()
    END_DATE_TIME = models.DateTimeField()


class Role(models.Model):

    # Visibility options for role (so the role's event schedule effectively)
    # Each level contains the previous; the levels also assume volunteers
    # don't have accounts, so everything outside of stuff is simply public
    ROLE_STAFF = "RL"  # Only the staff with the same role
    EVENT_STAFF = "ES"  # Event staff with any role
    PUBLIC = "PU"  # Everyone can see the role's schedule

    VISIBILITY_CHOICES = [(ROLE_STAFF, "Role Staff"),
                          (EVENT_STAFF, "Event Staff"),
                          (PUBLIC, "Public")]
    VISIBILITY = models.CharField(max_length=25, choices=VISIBILITY_CHOICES,
                                  default=ROLE_STAFF)

    NAME = models.CharField(max_length=25)
    EVENT = models.ForeignKey("Event", on_delete=models.CASCADE)

    # Aka whether the particular role is assinged hour-based shifts
    # or speedrun-based shifts
    HOUR_BASED = models.BooleanField(default=False)
