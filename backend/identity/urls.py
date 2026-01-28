from django.urls import path
from . import views

urlpatterns = [
    path('/identity', views.index, name='index'),
]

