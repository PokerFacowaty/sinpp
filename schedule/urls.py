from django.urls import path
from . import views

urlpatterns = [
    path('upload_csv/', views.upload_csv, name="upload_csv"),
    path('add_event/', views.add_event, name="add_event"),
    path('schedule/<str:event>/<str:room>/', views.schedule, name='schedule'),
    path('', views.index, name='main')
]