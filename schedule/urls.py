from django.urls import path
from . import views

urlpatterns = [
    path('upload_csv/', views.upload_csv, name="upload_csv"),
    path('add_event/', views.add_event, name="add_event"),
    path('remove_event/<int:event_id>/', views.remove_event),
    path('schedule/<str:event_slug>/<str:room_slug>/', views.room_schedule,
         name='room_schedule'),
    # path('schedule/<int:event_id>/', views.event_schedule,
    #  name='room_schedule'),
    path('shift/<int:shift_id>/', views.shift),
    path('add_shift/', views.add_shift),
    path('remove_shift/<int:shift_id>/', views.remove_shift),
    path('edit_shift/<int:shift_id>/', views.edit_shift),
    path('event/<str:event_slug>/', views.event, name='event'),
    path('edit_event/<str:event_slug>/', views.edit_event),
    path('add_role/<int:event_id>/', views.add_role, name='add_role'),
    path('remove_role/<int:role_id>', views.remove_role, name='remove_role'),
    path('role/<int:role_id>/', views.role, name='role'),
    path('edit_role/<int:role_id>/', views.edit_role, name='edit_role'),
    path('all_usernames/', views.all_usernames),
    path('add_staff/<int:event_id>/', views.add_staff, name='add_staff'),
    path('remove_staff/<int:event_id>/', views.remove_staff,
         name='remove_staff'),
    path('', views.index, name='main')
]
