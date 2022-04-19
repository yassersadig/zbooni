from django.urls import path
from . import api_views
from rest_framework.routers import DefaultRouter

router = DefaultRouter()
router.register(r'accounts', api_views.UserViewSet, basename='account')

urlpatterns = [
    *router.urls,
    path('accounts/create', api_views.UserRegistration.as_view()),
    path('accounts/activate/<uid>/<confirmation_token>', api_views.UserActivation.as_view(), name='account_activate'),
    path('accounts/login', api_views.UserLogin.as_view()),
    path('accounts/change_password', api_views.UserChangePassword.as_view())
]
