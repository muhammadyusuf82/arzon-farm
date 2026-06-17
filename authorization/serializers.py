from rest_framework import serializers
from django.contrib.auth import get_user_model

User = get_user_model()

class SignUpSerializer(serializers.ModelSerializer):
    """
    This serializer is only for creating users
    """

    class Meta:
        model = User
        fields = ['phone_number', 'email', 'metadata', 'password']

    def create(self, validated_data):
        validated_data.update({'username': validated_data['phone_number']})
        return User.objects.create_user(**validated_data)

class UpdateUserDataSerializer(serializers.ModelSerializer):
    """
    This serializer is for updating user data
    """

    class Meta:
        model = User
        fields = ['email', 'metadata']

    def create(self, validated_data):
        raise Exception('WHAT ARE YOU DOING???! DO NOT CREATE USERS HERE!!')
    

    