from django.contrib import admin
from django.urls import path
from . import views

urlpatterns = [
    path('',views.getcode,name="getcode"),
    path('reset/',views.reset,name="reset")
]