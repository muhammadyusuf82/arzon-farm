from authorization.serializers import (
    SignUpSerializer,
    UpdateUserDataSerializer,
    UserSerializer,
    ChangePasswordSerializer,
)
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAdminUser, AllowAny, IsAuthenticated
from rest_framework.viewsets import ModelViewSet
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import get_user_model

User = get_user_model()


def _tokens_for_user(user):
    refresh = RefreshToken.for_user(user)
    return {
        'refresh': str(refresh),
        'access': str(refresh.access_token),
    }


@api_view(['POST'])
@permission_classes([AllowAny])
def register(request):
    """
    Create a user if the phone number is not already taken.
    Returns JWT tokens on success.
    """
    serializer = SignUpSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    user = serializer.save()
    return Response(
        {
            'detail': 'user created successfully',
            'code': 'signup_success',
            **_tokens_for_user(user),
            'user': {
                'id': user.id,
                'phone_number': user.phone_number,
                'email': user.email,
                'role': user.role,
                'metadata': user.metadata,
            },
        },
        status=status.HTTP_201_CREATED,
    )


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def change_password(request):
    serializer = ChangePasswordSerializer(data=request.data, context={'request': request})
    serializer.is_valid(raise_exception=True)
    serializer.save()
    return Response(
        {'detail': 'password updated successfully', 'code': 'success'},
        status=status.HTTP_200_OK,
    )


@api_view(['PUT', 'PATCH'])
@permission_classes([IsAuthenticated])
def update_profile(request):
    partial = request.method == 'PATCH'
    serializer = UpdateUserDataSerializer(request.user, data=request.data, partial=partial)
    serializer.is_valid(raise_exception=True)
    serializer.save()
    return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def view_profile(request):
    return Response({
        'id': request.user.id,
        'phone_number': request.user.phone_number,
        'role': request.user.role,
        'metadata': request.user.metadata,
        'email': request.user.email,
        'is_staff': request.user.is_staff,
        'is_superuser': request.user.is_superuser,
    })


class UsersViewSet(ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAdminUser]
