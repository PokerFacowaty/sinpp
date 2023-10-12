from django.urls import path
from . import views

urlpatterns = [
    path('upload_csv/', views.upload_csv, name="upload_csv"),
    path('add_event/', views.add_event, name="add_event"),
    path('schedule/<str:event>/<str:room>/', views.schedule, name='schedule'),
    path('shift/<int:shift_id>/', views.shift),
    path('add_shift/', views.add_shift),
    path('', views.index, name='main')
]
