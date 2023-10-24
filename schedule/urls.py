from django.urls import path
from . import views

urlpatterns = [
    path('upload_csv/', views.upload_csv, name="upload_csv"),
    path('add_event/', views.add_event, name="add_event"),
    path('remove_event/<int:event_id>/', views.remove_event),
    path('schedule/<int:event_id>/<int:room_id>/', views.schedule,
         name='schedule'),
    path('shift/<int:shift_id>/', views.shift),
    path('add_shift/', views.add_shift),
    path('remove_shift/<int:shift_id>/', views.remove_shift),
    path('edit_shift/<int:shift_id>/', views.edit_shift),
    path('event/<int:event_id>/', views.event, name='event'),
    path('edit_event/<int:event_id>/', views.edit_event),
    path('', views.index, name='main')
]
