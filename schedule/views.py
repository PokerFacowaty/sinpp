from django.shortcuts import render, redirect, get_object_or_404
from django.http import (JsonResponse, HttpResponseNotFound,
                         HttpResponseForbidden, HttpResponseBadRequest)
from .forms import UploadCSVForm
from schedule.parse_schedule_csv import parse_oengus, handle_uploaded_file
from .models import (EventForm, Event, Room, Speedrun, Shift, Intermission,
                     Role, RoleForm, Person)
from django.contrib.auth.models import Group, User
from django.contrib.auth.decorators import login_required
import math
from datetime import timedelta
import json
from django.core import serializers
from django.views.decorators.csrf import ensure_csrf_cookie

# NOTE TO SELF ON THE ORDER OF OPERATIONS:
# if object exists (NotFound / 404)
# if user has permissions for object (Forbidden / 403)
# if the request is right (BadRequest, 400)

'''The naming convention for CRUD operations is: add_thing, thing, edit_thing,
remove_thing.'''


def index(request):
    return render(request, 'schedule/base_main.html')


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
    return render(request, "schedule/base_parse_csv.html", {"form": form})


@login_required
def add_event(request):
    if request.method == "POST":
        form = EventForm(request.POST)
        if form.is_valid():
            cl = form.cleaned_data
            ev = Event.create(cl["NAME"], cl["SLUG"],
                              cl["START_DATE_TIME"], cl["END_DATE_TIME"])
            ev.save()
            grp = Group.objects.get(name=cl["SLUG"] + " Staff")
            usr = User.objects.get(username=request.user)
            grp.user_set.add(usr)
            return redirect('user_profile')
    elif request.method == "GET":
        form = EventForm()
        return render(request, "schedule/base_add_event.html", {"form": form})
    return HttpResponseBadRequest()


@ensure_csrf_cookie
@login_required
def event(request, event_slug):
    events = Event.objects.filter(SLUG=event_slug)
    if events:
        ev = events[0]
        usr = User.objects.get(username=request.user)
        if usr.has_perm('event.view_event', ev):
            if request.method == "GET":
                ev.roles = Role.objects.filter(EVENT=ev)
                ev.staff = User.objects.filter(groups__name=ev.STAFF)
                ev.rooms = Room.objects.filter(EVENT=ev)
                content = {'event': ev}
                return render(request, 'schedule/base_event.html', content)
            return HttpResponseBadRequest()
        return HttpResponseForbidden()
    return HttpResponseNotFound()


@login_required
def edit_event(request, event_slug):
    events = Event.objects.filter(SLUG=event_slug)
    if events:
        usr = User.objects.get(username=request.user)
        ev = events[0]
        if usr.has_perm('event.edit_event', ev):
            if request.method == "POST":
                form = EventForm(request.POST, instance=ev)
                if form.is_valid():
                    form.save()
                    return redirect("event", event_slug=event_slug)
                return HttpResponseBadRequest()
            elif request.method == "GET":
                form = EventForm(instance=ev)
                return render(request, "schedule/base_edit_event.html",
                              {'form': form, 'event': ev})
            return HttpResponseBadRequest()
        return HttpResponseForbidden()
    return HttpResponseNotFound()


@login_required
def remove_event(request, event_slug):
    '''The confirmation page for a GET request and actual removal for POST'''
    usr = User.objects.get(username=request.user)
    events = Event.objects.filter(SLUG=event_slug)
    if events:
        ev = events[0]
        if usr.has_perm('event.remove_event', ev):
            if request.method == "GET":
                return render(request, 'schedule/base_remove_event.html',
                              {'event': ev})
            elif request.method == "POST":
                ev.delete()
                return redirect("user_profile")
            return HttpResponseBadRequest()
        return HttpResponseForbidden()
    return HttpResponseNotFound()


@login_required
def add_role(request, event_slug):
    usr = User.objects.get(username=request.user)
    events = Event.objects.filter(SLUG=event_slug)
    if events:
        ev = events[0]
        if usr.has_perm('event.add_role', ev):
            if request.method == "POST":
                form = RoleForm(request.POST)
                if form.is_valid():
                    cl = form.cleaned_data
                    tsm = cl['TIME_SAFETY_MARGIN']
                    rl = Role.objects.create(NAME=cl['NAME'],
                                             TIME_SAFETY_MARGIN=tsm,
                                             EVENT=ev)
                    rl.save()
                    return redirect('event', event_slug=ev.SLUG)
            elif request.method == "GET":
                form = RoleForm()
                return render(request, 'schedule/base_add_role.html',
                              {'form': form})
            return HttpResponseBadRequest()
        return HttpResponseForbidden()
    return HttpResponseNotFound()


@login_required
def role(request, role_id):
    roles = Role.objects.filter(pk=role_id)
    if roles:
        rl = roles[0]
        ev = rl.EVENT
        usr = User.objects.get(username=request.user)
        if usr.has_perm('event.view_role', ev):
            if request.method == "GET":
                rl.volunteers = Person.objects.filter(ROLES__in=[rl])
                content = {'role': rl}
                return render(request, 'schedule/base_role.html', content)
            return HttpResponseBadRequest()
        return HttpResponseForbidden()
    return HttpResponseNotFound()


@login_required
def edit_role(request, role_id):
    roles = Role.objects.filter(pk=role_id)
    if roles:
        usr = User.objects.get(username=request.user)
        rl = roles[0]
        if usr.has_perm('event.edit_role', rl.EVENT):
            if request.method == "POST":
                form = RoleForm(request.POST, instance=rl)
                if form.is_valid():
                    form.save()
                    return redirect("role", role_id=rl.id)
            elif request.method == "GET":
                form = RoleForm(instance=rl)
                return render(request, "schedule/base_edit_role.html",
                              {'form': form, 'role': rl})
            return HttpResponseBadRequest()
        return HttpResponseForbidden()
    return HttpResponseNotFound()


@login_required
def remove_role(request, role_id):
    '''The confirmation page for a GET request and actual removal for DELETE'''
    roles = Role.objects.filter(pk=role_id)
    if roles:
        rl = roles[0]
        usr = User.objects.get(username=request.user)
        ev = rl.EVENT
        if usr.has_perm('event.remove_role', ev):
            if request.method == "GET":
                return render(request, 'schedule/base_remove_role.html',
                              {'role': rl})
            elif request.method == "POST":
                rl.delete()
                return redirect('event', event_slug=ev.SLUG)
            return HttpResponseBadRequest()
        return HttpResponseForbidden()
    return HttpResponseNotFound()


@login_required
@ensure_csrf_cookie
def room_schedule(request, event_slug, room_slug):
    '''Show the schedule for a particular Room of the Event.'''
    ev = get_object_or_404(Event, SLUG=event_slug)
    rm = get_object_or_404(Room, EVENT=ev, SLUG=room_slug)
    usr = User.objects.get(username=request.user)

    if request.method == "GET":
        if usr.has_perm('event.view_event', ev):
            runs = Speedrun.objects.filter(EVENT=ev, ROOM=rm)
            interms = Intermission.objects.filter(EVENT=ev, ROOM=rm)
            ev_roles = Role.objects.filter(EVENT=ev)
            ev_start = ev.START_DATE_TIME
            ev_end = ev.END_DATE_TIME

            role_shifts = {x: [y for y in Shift.objects.filter(EVENT=ev,
                                                               ROOM=rm,
                                                               ROLE=x)]
                           for x in ev_roles}
            for role in role_shifts.values():
                for sh in role:
                    # Lower case for things added here and not in the model
                    sh.volunteer_names = sh.VOLUNTEERS.all()
                    sh.start_mins_rel = ((sh.START_DATE_TIME
                                          - ev_start).total_seconds() // 60)
                    sh.length_mins_rel = math.ceil(
                        (sh.END_DATE_TIME
                         - sh.START_DATE_TIME).total_seconds() // 60)
                    sh.start_iso = sh.START_DATE_TIME.isoformat()
                    sh.end_iso = sh.END_DATE_TIME.isoformat()

            timed_runs = [{'type': 'run',
                           'obj': x,
                           'start_mins_rel': ((x.START_DATE_TIME
                                              - ev_start).total_seconds()
                                              // 60),
                           'length_mins_rel': math.ceil(
                                              x.ESTIMATE.total_seconds()
                                              // 60)}
                          for x in runs]
            timed_interms = [{'type': 'interm',
                              'obj': x,
                              'start_mins_rel': ((x.START_DATE_TIME
                                                 - ev_start).total_seconds()
                                                 // 60),
                              'length_mins_rel': math.ceil(
                                                 x.DURATION.total_seconds()
                                                 // 60)}
                             for x in interms]

            runs_interms = [x for x in timed_runs]
            runs_interms.extend(timed_interms)
            runs_interms.sort(key=lambda x: x["obj"].START_DATE_TIME)

            # This means you can technically start a shift before the event
            # starts, but validation should take care of that.
            table_start = (ev_start
                           - timedelta(minutes=ev_start.minute,
                                       seconds=ev_start.second,
                                       microseconds=ev_start.microsecond))
            table_end = (ev_end + timedelta(hours=1)
                         - timedelta(minutes=ev_end.minute,
                                     seconds=ev_end.second,
                                     microseconds=ev_end.microsecond))
            times = []
            t = table_start
            while t <= table_end:
                times.append(t.isoformat(sep="\n").split("+")[0])
                t += timedelta(hours=1)

            content = {'room': rm, 'runs_interms': runs_interms,
                       'times': times,
                       'shifts': role_shifts,
                       'table_start': table_start.isoformat(),
                       'table_end': table_end.isoformat()}
            return render(request, 'schedule/base_schedule.html', content)
        return HttpResponseForbidden()
    return HttpResponseBadRequest()


# # # # # # # #
# AJAX views  #
# # # # # # # #


@login_required
def add_shift(request):
    # TODO: people
    data = json.load(request)
    shift = data.get('payload')
    events = Event.objects.filter(pk=int(shift['EVENT']))
    if events:
        ev = events[0]
        usr = User.objects.get(username=request.user)
        if usr.has_perm('event.add_shift', ev):
            is_ajax = (request.headers.get("X-Requested-With")
                       == "XMLHttpRequest")
            if is_ajax and request.method == "POST":
                new_shift = Shift.objects.create(
                                ROLE=Role.objects.get(pk=int(shift['ROLE'])),
                                EVENT=ev,
                                ROOM=Room.objects.get(pk=int(shift['ROOM'])),
                                START_DATE_TIME=shift['START_DATE_TIME'],
                                END_DATE_TIME=shift['END_DATE_TIME'])
                new_shift.save()
                return JsonResponse({'status': 'Shift added!',
                                     'context': {'id': new_shift.id}})
            return JsonResponse({'context': 'Ivalid request'}, status=400)
        return JsonResponse({'context': 'Permission denied'}, status=403)
    return JsonResponse({'context': 'Event not found'}, status=404)


@login_required
def shift(request, shift_id):
    shifts = Shift.objects.filter(pk=shift_id)
    if shifts:
        shift = shifts[0]
        ev = shift.EVENT
        usr = User.objects.get(username=request.user)
        if usr.has_perm('event.view_shift', ev):
            is_ajax = (request.headers.get("X-Requested-With")
                       == "XMLHttpRequest")
            if is_ajax and request.method == "GET":
                data = serializers.serialize('json', [shift])
                # [1:-1] so that it's a single object
                return JsonResponse({'context': data[1:-1]})
            return JsonResponse({'context': 'Invalid request.'}, status=400)
        return JsonResponse({'context': 'Permission denied'}, status=403)
    return JsonResponse({'context': "Shift not found"}, status=404)


@login_required
def edit_shift(request, shift_id):
    shifts = Shift.objects.filter(pk=shift_id)
    if shifts:
        shift = shifts[0]
        ev = shift.EVENT
        usr = User.objects.get(username=request.user)
        if usr.has_perm('event.edit_shift', ev):
            is_ajax = (request.headers.get("X-Requested-With")
                       == "XMLHttpRequest")
            if is_ajax and request.method == "PUT":
                data = json.load(request)
                payload = data.get('payload')
                for k, v in payload.items():
                    setattr(shift, k, v)
                shift.save()
                return JsonResponse({'context': 'Shift updated'})
            return JsonResponse({'context': 'Invalid request'}, status=400)
        return JsonResponse({'context': 'Permission denied'}, status=403)
    return JsonResponse({'context': 'Shift not found'}, status=404)


@login_required
def remove_shift(request, shift_id):
    # using filter instead of get since filter will just return an empty query
    # I have a check for, get would throw an error

    # technically the [0] isn't needed since as long as you don't retrieve all
    # the objects .delete() works on every item in the query, but I wanted to
    # be precise (refuses to work for .all() as a safety measure)
    shifts = Shift.objects.filter(pk=shift_id)
    if shifts:
        usr = User.objects.get(username=request.user)
        shift = shifts[0]
        ev = shift.EVENT
        if usr.has_perm('event.remove_shift', ev):
            is_ajax = (request.headers.get("X-Requested-With")
                       == "XMLHttpRequest")
            if is_ajax and request.method == "DELETE":
                shift.delete()
                return JsonResponse({'context': 'Shift deleted'})
            return JsonResponse({'context': 'Invalid request'}, status=400)
        return JsonResponse({'context': 'Permission denied'}, status=403)
    return JsonResponse({'context': 'Shift not found'}, status=404)


@login_required
def add_staff(request, event_id):
    events = Event.objects.filter(pk=event_id)
    if events:
        ev = events[0]
        usr = User.objects.get(username=request.user)
        if usr.has_perm('event.add_staff', ev):
            is_ajax = (request.headers.get("X-Requested-With")
                       == "XMLHttpRequest")
            if is_ajax and request.method == "POST":
                data = json.load(request)
                username = data.get('payload')["username"]
                new_staff_member = User.objects.filter(username=username)
                if new_staff_member:
                    new_staff_member = new_staff_member[0]
                    staff_group = ev.STAFF
                    if not new_staff_member.groups.filter(
                            name=ev.STAFF.name).exists():
                        staff_group.user_set.add(new_staff_member)
                        return JsonResponse({'context': 'Staff member added'})
                    return JsonResponse({'context':
                                        'User is already a staff member'},
                                        status=409)
                return JsonResponse({'context':
                                    f"The user {username} doesn't exist"},
                                    status=404)
            return JsonResponse({'context': 'Invalid request'}, status=400)
        return JsonResponse({'context': 'Permission denied'}, status=403)
    return JsonResponse({'context': 'Event not found'}, status=404)


@login_required
def remove_staff(request, event_id):
    data = json.load(request)
    staff_member_username = data.get('payload')["username"]
    staff_members = User.objects.filter(username=staff_member_username)
    if staff_members:
        staff_member = staff_members[0]
        events = Event.objects.filter(pk=event_id)
        if events:
            ev = events[0]
            usr = User.objects.get(username=request.user)
            if usr.has_perm('event.remove_staff', ev):
                staff_group = ev.STAFF
                is_ajax = (request.headers.get("X-Requested-With")
                           == "XMLHttpRequest")
                if is_ajax and request.method == "DELETE":
                    if staff_member.groups.filter(
                         name=staff_group.name).exists():
                        staff_group.user_set.remove(staff_member)
                        return JsonResponse({'context': ('User succesfully'
                                            + 'removed from staff')})
                    return JsonResponse({'context': ('The user requested to be'
                                        + 'removed from staff is not its'
                                        + 'member')}, status=409)
                return JsonResponse({'context': 'Invalid request'}, status=400)
            return JsonResponse({'context': 'Permission denied'}, status=403)
        return JsonResponse({'context': 'Event not found'}, status=404)
    return JsonResponse({'context': 'Staff member not found in users'},
                        status=404)


@login_required
def all_usernames(request):
    users = User.objects.all()
    # Never a case of no users because login_required
    is_ajax = (request.headers.get("X-Requested-With")
               == "XMLHttpRequest")
    if is_ajax and request.method == "GET":
        pks_names = [[user.id, user.username] for user in users]
        data = json.dumps(pks_names)
        return JsonResponse({'context': data})
    return JsonResponse({'context': 'Invalid request.'}, status=400)
