from django.shortcuts import render
from django.http import HttpResponseRedirect
from .forms import UploadCSVForm
from schedule.parse_schedule_csv import parse_oengus, handle_uploaded_file
from .models import EventForm, Event, Room, Speedrun, Shift
from django.contrib.auth.models import Group, User
from django.contrib.auth.decorators import login_required
from rules import has_perm
from django.core.exceptions import PermissionDenied


def index(request):
    return render(request, 'schedule/main.html')

# TODO: forms need a success / failure screen


@login_required
def upload_csv(request):
    usr = User.objects.get(username=request.user)
    groups = usr.groups.all()
    if request.method == "POST":
        form = UploadCSVForm(request.POST, request.FILES, data={'groups': groups})
        print(form.errors)
        if form.is_valid():
            event = form.cleaned_data['event']
            room = form.cleaned_data.get('room', None)
            filepath = handle_uploaded_file(request.FILES['file_'], "Oengus")
            parse_oengus(filepath, event, room)
    else:
        form = UploadCSVForm(data={'groups': groups})
    return render(request, "schedule/parse_csv.html", {"form": form})


@login_required
def add_event(request):
    if request.method == "POST":
        form = EventForm(request.POST)
        if form.is_valid():
            cl = form.cleaned_data
            ev = Event.create(cl["NAME"], cl["SHORT_TITLE"],
                              cl["START_DATE_TIME"], cl["END_DATE_TIME"])
            ev.save()
            grp = Group.objects.get(name=cl["SHORT_TITLE"] + " Staff")
            usr = User.objects.get(username=request.user)
            grp.user_set.add(usr)
    else:
        form = EventForm()
    return render(request, "schedule/add_event.html", {"form": form})


@login_required
def schedule(request, event, room):
    ev = Event.objects.get(SHORT_TITLE=event)
    rm = Room.objects.get(EVENT=ev, SLUG=room)
    runs = Speedrun.objects.filter(EVENT=ev, ROOM=rm).order_by("START_TIME")
    usr = User.objects.get(username=request.user)
    shifts = Shift.objects.filter(EVENT=ev, ROOM=rm)
    if usr.has_perm('event.view_event', ev):
        content = {'room': rm, 'speedruns': runs, 'shifts': shifts}
        print(runs)
        return render(request, 'schedule/base_schedule.html', content)
    else:
        raise PermissionDenied()
