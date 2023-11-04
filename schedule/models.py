from django.db import models
from datetime import timedelta, datetime
from django.db.models import Q
from django.forms import ModelForm, DateTimeInput
from rules.contrib.models import RulesModel
from rules import predicate, add_perm
from django.contrib.auth.models import Group


class Event(RulesModel):
    '''The SLUG is unique and non-nullable to make it possible to reference
    events by it'''

    NAME = models.CharField(max_length=100)
    SLUG = models.SlugField(max_length=25, unique=True, null=False)
    START_DATE_TIME = models.DateTimeField()
    END_DATE_TIME = models.DateTimeField()
    STAFF = models.ForeignKey(Group, related_name="staff_of",
                              on_delete=models.CASCADE)

    @classmethod
    def create(cls, NAME, SLUG, START_DATE_TIME, END_DATE_TIME):
        Group.objects.create(name=SLUG + " Staff")
        staff_group = Group.objects.get(name=SLUG + " Staff")
        event = cls(NAME=NAME, SLUG=SLUG,
                    START_DATE_TIME=START_DATE_TIME,
                    END_DATE_TIME=END_DATE_TIME, STAFF=staff_group)
        return event

    @predicate
    def is_event_staff(user, event):
        return user.groups.filter(name=event.STAFF).exists()

    '''The naming convention for CRUD in perms is: add_thing, view_thing,
    edit_thing, remove_thing.'''

    # Anyone can add events
    add_perm('event.view_event', is_event_staff)
    add_perm('event.edit_event', is_event_staff)
    add_perm('event.remove_event', is_event_staff)

    add_perm('event.add_shift', is_event_staff)
    add_perm('event.view_shift', is_event_staff)
    add_perm('event.edit_shift', is_event_staff)
    add_perm('event.remove_shift', is_event_staff)

    add_perm('event.add_role', is_event_staff)
    add_perm('event.view_role', is_event_staff)
    add_perm('event.edit_role', is_event_staff)
    add_perm('event.remove_role', is_event_staff)

    add_perm('event.add_staff', is_event_staff)
    add_perm('event.remove_staff', is_event_staff)

    def __str__(self) -> str:
        return self.NAME


class EventForm(ModelForm):
    class Meta:
        model = Event
        fields = ['NAME', 'SLUG', 'START_DATE_TIME', 'END_DATE_TIME']
        widgets = {"START_DATE_TIME": DateTimeInput(
                                      attrs={'type': 'datetime-local'}),
                   "END_DATE_TIME": DateTimeInput(
                                   attrs={'type': 'datetime-local'})}


class Room(models.Model):
    '''Basically a stream in case of a traditional speedrunning marathon.
       The idea of rooms makes it more general and also probably easier to
       understand - a volunteer cannot be in two separate rooms at the same
       time, be it physical rooms, streams or voice chats.

       Room's SLUG is not needed to be unique (since that'd mean 'Stream 1' can
       only be used once globally), but because of that Rooms need to be
       referenced by their SLUG AND their parent event.'''

    EVENT = models.ForeignKey(Event, on_delete=models.CASCADE)
    NAME = models.CharField(max_length=100)
    SLUG = models.SlugField(max_length=25, null=False)

    def __str__(self) -> str:
        return self.NAME + f' ({self.EVENT})'


class Speedrun(models.Model):

    EVENT = models.ForeignKey(Event, on_delete=models.CASCADE)
    # The room functionality should be optional, so that it's not a pain
    # for anyone who doesn't need it
    ROOM = models.ForeignKey(Room, on_delete=models.SET_NULL, null=True)
    GAME = models.CharField(max_length=100)
    CATEGORY = models.CharField(max_length=100, blank=True)

    # any volunteers taking part as runners, commentators
    VOLUNTEERS_ENGAGED = models.ManyToManyField(
                                        "Person",
                                        related_name="SPEEDRUNS_ENGAGED_IN")

    START_DATE_TIME = models.DateTimeField()
    ESTIMATE = models.DurationField()
    END_DATE_TIME = models.DateTimeField()

    def save(self, *args, **kwargs):
        if self.END_DATE_TIME is None and self.ESTIMATE is not None:
            self.END_DATE_TIME = self.START_DATE_TIME + self.ESTIMATE
        elif self.END_DATE_TIME is not None and self.ESTIMATE is None:
            self.ESTIMATE = self.END_DATE_TIME - self.START_DATE_TIME
        super(Speedrun, self).save(*args, **kwargs)

    def __str__(self) -> str:
        result = self.GAME + f' [{self.CATEGORY}]'
        if self.ROOM:
            result += f' ({self.ROOM})'
        result += f' ({self.EVENT})'
        return result


class Intermission(models.Model):

    EVENT = models.ForeignKey(Event, on_delete=models.CASCADE)
    ROOM = models.ForeignKey(Room, on_delete=models.SET_NULL, null=True)
    START_DATE_TIME = models.DateTimeField()
    DURATION = models.DurationField()
    END_DATE_TIME = models.DateTimeField()

    def save(self, *args, **kwargs):
        if self.END_DATE_TIME is None and self.DURATION is not None:
            self.END_DATE_TIME = self.START_DATE_TIME + self.DURATION
        elif self.END_DATE_TIME is not None and self.DURATION is None:
            self.DURATION = self.END_DATE_TIME - self.START_DATE_TIME
        super(Intermission, self).save(*args, **kwargs)

        def __str__(self) -> str:
            result = f'Intermission @ {self.START_DATE_TIME}'
            if self.ROOM:
                result += f' ({self.ROOM})'
            else:
                result += f' ({self.EVENT})'
            return result


class Shift(models.Model):
    '''A single shift of one or more volunteers'''

    VOLUNTEERS = models.ManyToManyField("Person")
    ROLE = models.ForeignKey("Role", on_delete=models.CASCADE)
    EVENT = models.ForeignKey("Event", on_delete=models.CASCADE)
    ROOM = models.ForeignKey(Room, on_delete=models.SET_NULL, null=True)
    START_DATE_TIME = models.DateTimeField()
    END_DATE_TIME = models.DateTimeField()

    SPEEDRUNS = models.ManyToManyField("Speedrun", blank=True)

    def __str__(self) -> str:
        result = (f'{", ".join([x.NICKNAME for x in self.VOLUNTEER.all()])}'
                  + f'@ {self.START_DATE_TIME}')
        if self.ROOM:
            result += f' ({self.ROOM})'
        else:
            result += f' ({self.EVENT})'
        return result


class Person(models.Model):
    NICKNAME = models.CharField(max_length=25)
    PRONOUNS = models.CharField(max_length=25, blank=True)
    ROLES = models.ManyToManyField("Role", blank=True)

    def is_available(self, start_time: datetime, end_time: datetime,
                     role) -> bool:
        '''Whether the current start_time and end_time are within a Person's
           availability block. Not to be confused with is_free(), which checks
           if a Person is already doing a shift at the event at that time.'''

        blocks = AvailabilityBlock.objects.filter(PERSON=self)
        margin = role.TIME_SAFETY_MARGIN
        for bl in blocks:
            if ((start_time - bl.START_DATE_TIME) > margin
               and (bl.END_DATE_TIME - end_time) > margin):
                return True
        return False

    def is_busy(self, start_time: datetime, end_time: datetime) -> bool:
        '''Returns whether the person is already on shift at the specified
           time.'''
        # Get all shifts of that person where its end is later than the
        # start_time OR its start is earlier than end_time
        # TODO: add also checking against all the speedruns the volunteer is
        # engaged in
        shifts = Shift.objects.filter(Q(VOLUNTEER__in=[self]),
                                      Q(END_DATE_TIME__gt=start_time)
                                      | Q(START_DATE_TIME__lt=end_time))
        return False if shifts else True

    def __str__(self) -> str:
        return self.NICKNAME


class AvailabilityBlock(models.Model):
    PERSON = models.ForeignKey("Person", on_delete=models.CASCADE)
    EVENT = models.ForeignKey("Event", on_delete=models.CASCADE)
    START_DATE_TIME = models.DateTimeField()
    END_DATE_TIME = models.DateTimeField()

    def __str__(self) -> str:
        return f"{self.PERSON} @ {self.START_DATE_TIME} ({self.EVENT})"


class Role(models.Model):
    '''Roles are made unique for every event (at least for now), since that
       allows for easier implementation of things like hour-based vs run-based,
       time safety margin etc'''

    # Visibility options for role (so the role's event schedule effectively)
    # Each level contains the previous; the levels also assume volunteers
    # don't have accounts, so everything outside of stuff is simply public
    PUBLIC = "PU"  # Everyone can see the role's schedule
    PRIVATE = "PR"  # Only event staff can see the role's schedule

    VISIBILITY_CHOICES = [(PRIVATE, "Private"),
                          (PUBLIC, "Public")]
    VISIBILITY = models.CharField(max_length=25, choices=VISIBILITY_CHOICES,
                                  default=PRIVATE)

    NAME = models.CharField(max_length=25)
    EVENT = models.ForeignKey("Event", on_delete=models.CASCADE)

    # Aka whether the particular role is assinged hour-based shifts,
    # speedrun-based shifts or intermission-based shifts

    HOUR_BASED = "HB"
    SPEEDRUN_BASED = "SB"
    INTERMISSION_BASED = "IB"

    TYPE_CHOICES = [(HOUR_BASED, "Hour-based"),
                    (SPEEDRUN_BASED, "Speedrun-based"),
                    (INTERMISSION_BASED, "Intermission-based")]
    TYPE = models.CharField(max_length=25, choices=TYPE_CHOICES,
                            default=HOUR_BASED)

    # How many minutes are added to each block before considering someone
    # available, setting this to 0 means that if a person's availability
    # starts at 15:00 and an activity starts at the same time, they're
    # considered available. Setting this to 15 means they have to be available
    # since at least 14:45 to be considered available for the activity.
    TIME_SAFETY_MARGIN = models.DurationField(default=timedelta(minutes=15))

    def __str__(self) -> str:
        return f"{self.NAME} ({self.EVENT})"


class RoleForm(ModelForm):
    class Meta:
        model = Role
        # I can already say TYPE and probably VISIBILITY will be depracated
        # soon, so ignoring them  for now - they have defaults anyway
        fields = ['NAME', 'TIME_SAFETY_MARGIN']
