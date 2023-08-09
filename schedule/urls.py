from django.urls import path
from . import views

urlpatterns = [
    path('upload_csv/', views.upload_csv, name="upload_csv"),
    path('', views.index, name='main')
]
