from rest_framework import serializers
from django.contrib.auth.models import User


class LimitedUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('first_name',)


class UserSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(required=True)
    password = serializers.CharField(required=True, write_only=True)

    class Meta:
        model = User
        fields = ('email', 'password', 'first_name', 'last_name')

    def save(self, **kwargs):
        user = User(
            first_name=self.validated_data['first_name'],
            last_name=self.validated_data['last_name'],
            email=self.validated_data['email'],
            username=self.validated_data['email'],
            is_active=False
        )
        user.set_password(self.validated_data['password'])
        user.save()
        return user
