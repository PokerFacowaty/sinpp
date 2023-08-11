from django.shortcuts import render
from django.http import HttpResponseRedirect
from .forms import UploadCSVForm
from schedule.parse_schedule_csv import parse_oengus, handle_uploaded_file
from .models import EventForm
from django.contrib.auth.models import Group
from django.contrib.auth.decorators import login_required


def index(request):
    return render(request, 'schedule/main.html')


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
            form.save()
            sh_tl = form.cleaned_data['SHORT_TITLE']
            Group.objects.create(name=sh_tl + " Staff")
    else:
        form = EventForm()
    return render(request, "schedule/add_event.html", {"form": form})
