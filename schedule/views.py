from django.shortcuts import render
from django.http import HttpResponseRedirect
from .forms import UploadCSVForm
from schedule.parse_schedule_csv import parse_oengus, handle_uploaded_file


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
