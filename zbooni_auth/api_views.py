from rest_framework.generics import CreateAPIView
from rest_framework.views import APIView
from django.contrib.auth.models import User
from .serializers import UserSerializer
from rest_framework.response import Response
from django.contrib.auth.tokens import default_token_generator
from django.contrib.sites.shortcuts import get_current_site
from rest_framework import status
from django.urls import reverse


class UserRegistration(CreateAPIView):
    serializer_class = UserSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        user = User.objects.get(email=serializer.data['email'])
        uid = user.pk
        confirmation_token = default_token_generator.make_token(user)
        current_site = get_current_site(request)
        activate_view_url = reverse('account_activate', kwargs={'uid': uid, 'confirmation_token': confirmation_token})
        activation_link = f'http://{current_site.domain}{activate_view_url}'
        user.email_user('Activate Your Account',
                        f'Please click on the link to confirm your registration: {activation_link}')
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)


class UserActivation(APIView):
    def get(self, request, uid, confirmation_token, format=None):
        error_message = False
        user = False
        try:
            user = User.objects.get(id=uid)

        except (TypeError, ValueError, OverflowError, User.DoesNotExist) as error:
            error_message = str(error)
        if not error_message and default_token_generator.check_token(user, confirmation_token):
            user.is_active = True
            user.save()
            return Response(UserSerializer(user).data)
        else:
            return Response({'Error': error_message})
