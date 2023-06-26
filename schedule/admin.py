from django.contrib import admin
from .models import Event, Speedrun, Shift, Person, AvailabilityBlock, Role

admin.site.register(Event)
admin.site.register(Speedrun)
admin.site.register(Shift)
admin.site.register(Person)
admin.site.register(AvailabilityBlock)
admin.site.register(Role)
