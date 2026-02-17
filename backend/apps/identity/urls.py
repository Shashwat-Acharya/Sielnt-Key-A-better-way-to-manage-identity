from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),  # Maps to /identity/ (defined in main urls.py)
]