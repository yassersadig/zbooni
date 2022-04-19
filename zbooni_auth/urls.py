from django.urls import path
from . import api_views

urlpatterns = [
    path('accounts/create', api_views.UserRegistration.as_view()),
]
