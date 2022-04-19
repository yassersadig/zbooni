from rest_framework.generics import CreateAPIView
from .serializers import UserSerializer, LimitedUserSerializer


class UserRegistration(CreateAPIView):
    serializer_class = UserSerializer
