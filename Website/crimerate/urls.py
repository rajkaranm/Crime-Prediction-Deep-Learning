from django.contrib import admin
from django.urls import path, include
from django.views.generic import TemplateView
from . import views

urlpatterns = [
    path('', include('core.urls')),
    path('crimerate', views.crimerate, name="crimerate")
]

