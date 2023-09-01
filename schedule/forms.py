from django import forms
from .models import Event, Room
from django.db.models import Q


class UploadCSVForm(forms.Form):
    title = forms.CharField(max_length=50)
    file_ = forms.FileField()
    # TODO: .all() just for testing
    # event = forms.ModelChoiceField(queryset=Event.objects.all())
    event = forms.ModelChoiceField(queryset=None)
    room = forms.ModelChoiceField(queryset=None)

    def __init__(self, *args, **kwargs):
        data = kwargs.pop('data', None)
        super(UploadCSVForm, self).__init__(*args, **kwargs)
        event_queryset = Event.objects.filter(Q(STAFF__in=data["groups"]))
        self.fields['event'].queryset = event_queryset
        self.fields['room'].queryset = Room.objects.filter(
                                       Q(EVENT__in=event_queryset))
