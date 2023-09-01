from django import forms
from .models import Event, Room
from django.db.models import Q


class UploadCSVForm(forms.Form):
    title = forms.CharField(max_length=50)
    file_ = forms.FileField()
    # TODO: .all() just for testing
    # event = forms.ModelChoiceField(queryset=Event.objects.all())
    event = forms.ModelChoiceField(queryset=None)
    room = forms.ModelChoiceField(queryset=Room.objects.all(), required=False)

    def __init__(self, *args, **kwargs):
        data = kwargs.pop('data', None)
        super(UploadCSVForm, self).__init__(*args, **kwargs)
        self.fields['event'].queryset = Event.objects.filter(
                                        Q(STAFF__in=data["groups"]))
