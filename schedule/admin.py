from django.contrib import admin
from .models import (Event, Speedrun, Shift, Person, AvailabilityBlock, Role,
                     Intermission)

admin.site.register(Event)
admin.site.register(Speedrun)
admin.site.register(Shift)
admin.site.register(Person)
admin.site.register(AvailabilityBlock)
admin.site.register(Role)
admin.site.register(Intermission)
