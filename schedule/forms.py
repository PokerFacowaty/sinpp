from django import forms
from .models import Event, Room


class UploadCSVForm(forms.Form):
    title = forms.CharField(max_length=50)
    file_ = forms.FileField()
    # TODO: .all() just for testing
    event = forms.ModelChoiceField(queryset=Event.objects.all())
    room = forms.ModelChoiceField(queryset=Room.objects.all(), required=False)
