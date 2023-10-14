from django.shortcuts import render
from django.http import (HttpResponseRedirect, JsonResponse,
                         HttpResponseBadRequest)
from .forms import UploadCSVForm
from schedule.parse_schedule_csv import parse_oengus, handle_uploaded_file
from .models import EventForm, Event, Room, Speedrun, Shift, Intermission, Role
from django.contrib.auth.models import Group, User
from django.contrib.auth.decorators import login_required
from rules import has_perm
from django.core.exceptions import PermissionDenied
import math
from datetime import timedelta
import json
from django.core import serializers
from django.views.decorators.csrf import ensure_csrf_cookie


def index(request):
    return render(request, 'schedule/main.html')

# TODO: forms need a success / failure screen


@login_required
def upload_csv(request):
    usr = User.objects.get(username=request.user)
    groups = usr.groups.all()
    if request.method == "POST":
        form = UploadCSVForm(request.POST, request.FILES,
                             data={'groups': groups})
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
@ensure_csrf_cookie
def schedule(request, event_id, room_id):
    ev = Event.objects.get(pk=event_id)
    rm = Room.objects.get(pk=room_id)
    usr = User.objects.get(username=request.user)

    # experimenting with [("run" or "interm", thing,
    # start in minutes since the start time, duration in minutes)]
    runs = Speedrun.objects.filter(EVENT=ev, ROOM=rm)
    interms = Intermission.objects.filter(EVENT=ev, ROOM=rm)
    ev_roles = Role.objects.filter(EVENT=ev)
    if runs[0].START_TIME < interms[0].START_TIME:
        start_time = runs[0].START_TIME
    else:
        start_time = interms[0].START_TIME
    role_shifts = {(x.NAME, x.id):
                   [y for y in Shift.objects.filter(EVENT=ev, ROOM=rm, ROLE=x)]
                   for x in ev_roles}
    for role in role_shifts.values():
        for sh in role:
            # Lower case for things added here and not in the model
            sh.volunteer_names = sh.VOLUNTEER.all()
            sh.start = ((sh.START_DATE_TIME
                         - start_time).total_seconds() // 60)
            sh.length = math.ceil((sh.END_DATE_TIME
                                   - sh.START_DATE_TIME).total_seconds() // 60)

    timed_runs = [{'type': 'run',
                   'obj': x,
                   'start': (x.START_TIME - start_time).total_seconds() // 60,
                   'length': math.ceil(x.ESTIMATE.total_seconds() // 60)}
                  for x in runs]
    timed_interms = [{'type': 'interm',
                      'obj': x,
                      'start': (
                          x.START_TIME - start_time).total_seconds() // 60,
                      'length': math.ceil(x.DURATION.total_seconds() // 60)}
                     for x in interms]

    runs_interms = []
    runs_interms = [x for x in timed_runs]
    runs_interms.extend(timed_interms)
    runs_interms.sort(key=lambda x: x["obj"].START_TIME)

    first_el_start = runs_interms[0]["obj"].START_TIME
    last_el_end = runs_interms[-1]["obj"].END_TIME
    table_start = (first_el_start
                   - timedelta(minutes=first_el_start.minute,
                               seconds=first_el_start.second,
                               microseconds=first_el_start.microsecond))
    table_end = (last_el_end
                 + timedelta(hours=1)
                 - timedelta(minutes=last_el_end.minute,
                             seconds=last_el_end.second,
                             microseconds=last_el_end.microsecond))
    times = []
    t = table_start
    while t <= table_end:
        times.append(t.isoformat(sep="\n").split("+")[0])
        t += timedelta(hours=1)

    if usr.has_perm('event.view_event', ev):
        # TODO: move this to the beginning so that no resources are wasted
        # when someone is not permitted
        content = {'room': rm, 'runs_interms': runs_interms, 'times': times,
                   'shifts': role_shifts, 'table_start': table_start.isoformat(),
                   'table_end': (table_end + timedelta(hours=1)).isoformat()}
        return render(request, 'schedule/base_schedule.html', content)
    else:
        raise PermissionDenied()


# NOTE: @login_required is HTML, so throws an error with JSON
@login_required
def shift(request, shift_id):
    shift = Shift.objects.filter(pk=shift_id)
    if not shift:
        return JsonResponse({'context': "Shift not found"}, status=404)

    usr = User.objects.get(username=request.user)
    ev = Shift.objects.get(pk=shift_id).EVENT
    if not usr.has_perm('shift.view_shift', ev):
        JsonResponse({'context': 'Permission denied'}, status=403)

    is_ajax = request.headers.get("X-Requested-With") == "XMLHttpRequest"

    if is_ajax:
        if request.method == "GET":
            data = serializers.serialize('json', shift)
            return JsonResponse({'context': data})

        return JsonResponse({'status': 'Invalid request.'}, status=400)
    else:
        return HttpResponseBadRequest('Invalid request')


def add_shift(request):
    if request.method == "POST":
        data = json.load(request)
        print(data)
        shift = data.get('payload')
        print(shift)
        new_shift = Shift.objects.create(
                                ROLE=Role.objects.get(pk=int(shift['ROLE'])),
                                EVENT=Event.objects.get(pk=int(shift['EVENT'])),
                                ROOM=Room.objects.get(pk=int(shift['ROOM'])),
                                START_DATE_TIME=shift['START_DATE_TIME'],
                                END_DATE_TIME=shift['END_DATE_TIME'])
        new_shift.save()
        return JsonResponse({'status': 'Shift added!',
                                'context': {'id': new_shift.id}})
