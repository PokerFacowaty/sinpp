from django.shortcuts import render
from django.http import HttpResponseRedirect
from .forms import UploadCSVForm
from schedule.parse_schedule_csv import parse_oengus, handle_uploaded_file
from .models import EventForm, Event
from django.contrib.auth.models import Group, User
from django.contrib.auth.decorators import login_required


def index(request):
    return render(request, 'schedule/main.html')

# TODO: forms need a success / failure screen


def upload_csv(request):
    if request.method == "POST":
        form = UploadCSVForm(request.POST, request.FILES)
        print(form.errors)
        if form.is_valid():
            event = form.cleaned_data['event']
            room = form.cleaned_data['room']
            filepath = handle_uploaded_file(request.FILES['file_'], "Oengus")
            parse_oengus(filepath, event)
    else:
        form = UploadCSVForm()
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
