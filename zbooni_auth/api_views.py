from rest_framework.generics import CreateAPIView
from rest_framework.views import APIView
from django.contrib.auth.models import User
from .serializers import UserSerializer, LimitedUserSerializer
from rest_framework.response import Response
from django.contrib.auth.tokens import default_token_generator
from django.contrib.sites.shortcuts import get_current_site
from rest_framework import status
from django.urls import reverse
from rest_framework.authtoken.models import Token
from rest_framework.permissions import IsAuthenticated
from rest_framework import viewsets
from django.shortcuts import get_object_or_404


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


class UserLogin(APIView):

    def post(self, request, format=None):
        email = request.data.get('email', False)
        password = request.data.get('password', False)
        if not (email and password):
            return Response({'Error': 'Both Email and Password are required!'})
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            return Response({'error': 'User not found!'})

        if not user.check_password(password):
            return Response({'Error': 'Incorrect password!'})

        token = Token.objects.get_or_create(user=user)
        return Response({'Access Token': token[0].key})


class UserChangePassword(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, format=None):
        uid = request.data.get('uid', False)
        password = request.data.get('password', False)
        if not (uid and password):
            return Response({'Error': 'Both User ID and the New Password are required!'})
        try:
            user = User.objects.get(id=uid)
        except User.DoesNotExist:
            return Response({'error': 'User not found!'})

        if request.user != user:
            return Response({'Error': 'A User Can Only Change their Own Password!'})

        user.set_password(password)
        user.save()
        return Response({'Success': "Password Changed Successfully!"})


class UserViewSet(viewsets.ViewSet):
    def list(self, request):
        serializer_class = UserSerializer if request.user.is_authenticated else LimitedUserSerializer
        queryset = User.objects.all()
        serializer = serializer_class(queryset, many=True)
        return Response(serializer.data)

    def retrieve(self, request, pk=None):
        serializer_class = UserSerializer if request.user.is_authenticated else LimitedUserSerializer
        queryset = User.objects.all()
        user = get_object_or_404(queryset, pk=pk)
        serializer = serializer_class(user)
        return Response(serializer.data)
