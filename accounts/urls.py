from os import name

from django.urls import path

from .views import ProfileAPIView

urlpatterns = [
    path("me/", ProfileAPIView.as_view(), name="my_profile"),
]