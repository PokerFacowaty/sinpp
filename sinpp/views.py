from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from schedule.views import index
from schedule.models import Event, Room, Role
from django.db.models import Q
from django.contrib.auth.models import User, Group
from django.http import HttpResponseBadRequest


@login_required
def user_profile(request):
    if request.method == "GET":
        usr = request.user
        usr_groups = usr.groups.all()
        usr_events = Event.objects.filter(Q(STAFF__in=usr_groups))
        for ev in usr_events:
            # lowercase to differentiate from DB values
            ev.roles = Role.objects.filter(EVENT=ev)
            ev.staff = User.objects.filter(groups__name=ev.STAFF)
            ev.rooms = Room.objects.filter(EVENT=ev)
        return render(request, 'registration/profile.html',
                      {'events': usr_events})
    return HttpResponseBadRequest()


def register_account(request):
    if request.method == "POST":
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect(index)
        return HttpResponseBadRequest()
    else:
        form = UserCreationForm()
        return render(request, 'registration/register.html', {'form': form})
