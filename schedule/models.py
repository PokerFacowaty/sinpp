from django.db import models


class Event(models.Model):

    NAME = models.CharField(max_length=100)
    SHORT_TITLE = models.CharField(max_length=25)
    START_DATE_TIME = models.DateTimeField()
    END_DATE_TIME = models.DateTimeField()


class Speedrun(models.Model):

    EVENT = models.ForeignKey(Event, on_delete=models.CASCADE)
    GAME = models.CharField()
    CATEGORY = models.CharField()

    # any volunteers taking part as runners, commentators
    VOLUNTEERS_RUNNING = models.ManyToManyField("Person")
    VOLUNTEERS_COMMENTATING = models.ManyToManyField("Person")

    VOLUNTEER_SHIFTS = models.ManyToManyField("Shift")
    START_TIME = models.DateTimeField()
    ESTIMATE = models.DurationField()
    END_TIME = models.DateTimeField()

    def save(self, *args, **kwargs):
        if self.END_TIME is None:
            self.END_TIME = self.START_TIME + self.ESTIMATE
        super(Speedrun, self).save(*args, **kwargs)


class Shift(models.Model):
    '''A single shift of a single volunteer'''

    VOLUNTEER = models.ForeignKey("Person", on_delete=models.CASCADE)
    ROLE = models.ForeignKey("Role", on_delete=models.CASCADE)
    START_DATE_TIME = models.DateTimeField()
    END_DATE_TIME = models.DateTimeField()


class Person(models.Model):
    NICKNAME = models.CharField()
    PRONOUNS = models.CharField()
    SPEEDRUNS = models.ManyToManyField(Speedrun)
    # PROFILES = models.ManyToManyField(SocialMediaProfile)
    ROLES = models.ManyToManyField("Role")


class AvailabilityBlock(models.Model):
    PERSON = models.ForeignKey(Person, on_delete=models.CASCADE)
    START_DATE_TIME = models.DateTimeField()
    END_DATE_TIME = models.DateTimeField()


class Role(models.Model):
    NAME = models.CharField()

    # Aka whether the particular role is assinged hour-based shifts
    # or speedrun-based shifts
    HOUR_BASED = models.BooleanField(default=False)
