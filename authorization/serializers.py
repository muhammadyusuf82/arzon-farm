from rest_framework import serializers
from django.contrib.auth.hashers import make_password
from django.contrib.auth import get_user_model

User = get_user_model()

class SignUpSerializer(serializers.ModelSerializer):
    """
    This serializer is only for creating users
    """

    class Meta:
        model = User
        fields = ['phone_number', 'email', 'metadata', 'password']
        extra_kwargs = {
            'password': {'write_only': True}
        }

class UpdateUserDataSerializer(serializers.ModelSerializer):
    """
    This serializer is for updating user data
    """

    class Meta:
        model = User
        fields = ['email', 'metadata']

    def create(self, validated_data):
        raise Exception('WHAT ARE YOU DOING???! DO NOT CREATE USERS HERE!!')
    
class UserSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = User
        fields = '__all__'
        extra_kwargs = {
            'password': {'write_only': True}
        }
    
    def update(self, instance, validated_data):
        if 'password' in validated_data:
            validated_data['password'] = make_password(validated_data['password'])
        return super().update(instance, validated_data)