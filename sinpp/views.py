from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from schedule.views import index
from schedule.models import Event, Room
from django.db.models import Q


@login_required
def user_profile(request):
    usr = request.user
    groups = usr.groups.all()
    events_rooms = {x: [] for x in Event.objects.filter(Q(STAFF__in=groups))}
    for ev in events_rooms.keys():
        events_rooms[ev] = [x for x in Room.objects.filter(EVENT=ev)]
    print(events_rooms)
    return render(request, 'registration/profile.html',
                  {'events_rooms': events_rooms})


def register_account(request):
    if request.method == "POST":
        form = UserCreationForm(request.POST)
        if form.is_valid():
            print("form valid")
            user = form.save()
            return redirect(index)
    else:
        form = UserCreationForm()
        return render(request, 'registration/register.html', {'form': form})
