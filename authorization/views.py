from authorization.serializers import SignUpSerializer, UpdateUserDataSerializer, UserSerializer
from authorization.send_sms import send_sms
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.permissions import IsAdminUser
from rest_framework.viewsets import ModelViewSet
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken
from core.settings import r, CODE_LENGTH, EXPIRES_IN, RESEND_IN
from django.contrib.auth import get_user_model
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt
import random
import uuid
from datetime import datetime

User = get_user_model()

# Create your views here.

format = '%Y-%m-%d %H:%M:%S.%f%z'

# ------- SIGN UP --------

@csrf_exempt
@api_view(['GET','POST'])
def begin_validation(request, phone_number):
    try:
        if User.objects.get(phone_number=phone_number):
            return Response({'detail': 'user with this phone number already exists', 'code': 'phone_number_exists'}, status=status.HTTP_400_BAD_REQUEST)
    except User.DoesNotExist:
        pass

    field =  'phone_validation:' + phone_number
    res = r.hgetall(field)
    if res != {}:
        renewal_time = datetime.strptime(res.get('created_at'), format) + RESEND_IN
        diff = renewal_time - timezone.now()
        if diff > timezone.timedelta(seconds=0):
            return Response(
                { 
                    'detail': 'a code was already sent',
                    'resend_time': str(renewal_time), 
                    'code': 'wait_to_resend' 
                }, status=status.HTTP_425_TOO_EARLY)
        r.delete(field)

    data = dict()
    data['code'] = "".join([str(random.randint(0,9)) for _ in range(CODE_LENGTH)])
    data['expires'] = str(timezone.now() + EXPIRES_IN)
    data['created_at'] = str(timezone.now())

    r.hset(field, mapping=data)

    send_sms(phone_number, data['code'])

    return Response({ 'detail': 'code sent successfully', 'code': 'code_sent_successfully' }, status=status.HTTP_200_OK)

@csrf_exempt
@api_view(['GET', 'POST'])
def validate_phone_number(request, phone_number, code):
    field = 'phone_validation:' + phone_number

    res = r.hgetall(field)
    if res == []:
        return Response(
            { 
                'detail': 'validation has not been requested with this phone number', 
                'code': 'no_validation_requested' 
            }, status=status.HTTP_400_BAD_REQUEST)
    
    if res.get('code') != code:
        return Response({
            'detail': 'incorrect code',
            'code': 'incorrect_code'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    if datetime.strptime(res.get('expires'), format) - timezone.now() < timezone.timedelta(seconds=0):
        return Response({
            'detail': "What's taking you so long? This code is already expired",
            'code': 'expired'
        }, status=status.HTTP_400_BAD_REQUEST)

    user_create_key = str(uuid.uuid4())
    r.set(f'user_create_key:{phone_number}', user_create_key)
    return Response(
        {
            'detail': 'Congratulations! Here is your user_create_key. If there was a previous one, it is already overwritten.', 
            'user_create_key': user_create_key, 
            'code': 'user_create_key_received'
        }, status=status.HTTP_200_OK)


@csrf_exempt
@api_view(['POST'])
def create_user_via_key(request, phone_number, user_create_key):
    real_user_create_key = r.get(f'user_create_key:{phone_number}')
    
    if user_create_key != real_user_create_key:
        return Response({
            'detail': 'wrong user create key',
            'code': 'wrong_user_create_key'
        }, status=status.HTTP_400_BAD_REQUEST)

    serializer = SignUpSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    serializer.save(phone_number=phone_number)

    refresh_token = RefreshToken.for_user(serializer.instance)

    return Response(
        { 
            'detail': 'I am soo proud of you!! These tokens are for all your effort!',
            'refresh': str(refresh_token),
            'access': str(refresh_token.access_token),
            'code': 'signup_success'
        }, status=status.HTTP_201_CREATED)

# ----- UPDATE PASSWORD ------

@csrf_exempt
@api_view(['GET', 'POST'])
def update_password_request(request):
    if not request.user.is_authenticated:
        return Response({ "detail": "Uhhhh, I'm sorry, do I know you?", 'code': 'not_authenticated' }, status=status.HTTP_403_FORBIDDEN)
    
    data = dict()
    data['code'] = "".join([str(random.randint(0,9)) for _ in range(CODE_LENGTH)])
    data['expires'] = str(timezone.now() + EXPIRES_IN)
    data['created_at'] = str(timezone.now())

    slot = r.hgetall(f'phone_number_update:{request.user.phone_number}')
    if slot != {}:
        renewal_time = datetime.strptime(slot.get('created_at'), format) + RESEND_IN
        if renewal_time - timezone.now() > timezone.timedelta(seconds=0):
            return Response({'resend_time': renewal_time, 'code': 'resend'}, status=status.HTTP_200_OK)
        r.delete(f'phone_number_update:{request.user.phone_number}')

    r.hset(f'phone_number_update:{request.user.phone_number}', mapping=data)

    send_sms(request.user.phone_number, data['code'])

    return Response({'detail': 'Check your SMS, the code should be there.', 'code': 'sent'}, status=status.HTTP_200_OK)

@csrf_exempt
@api_view(['GET', 'POST'])
def update_password(request, code, new_password):
    if not request.user.is_authenticated:
        return Response({ "detail": "Uhhhh, I'm sorry, do I know you?", 'code': 'not_authenticated' }, status=status.HTTP_401_UNAUTHORIZED)
    
    data = r.hgetall(f'phone_number_update:{request.user.phone_number}')

    if data == {}:
        return Response({'detail': 'this number either did not request a password update or the request is expired', 'code': 'no_code_found'}, status=status.HTTP_400_BAD_REQUEST)
    
    if data.get('code') != code:
        return Response({'detail': 'wrong code', 'code': 'incorrect_code'}, status=status.HTTP_200_OK)

    if datetime.strptime(data.get('expires'), format) - timezone.now() < timezone.timedelta(seconds=0):
        return Response({
            'detail': "What's taking you so long? This code is already expired",
            'code': 'expired'
        }, status=status.HTTP_400_BAD_REQUEST)

    request.user.set_password(new_password)
    request.user.save()

    return Response({ 'detail': 'your new password has been set', 'code': 'success' }, status=status.HTTP_200_OK)

# ----- MISC -------

@csrf_exempt
@api_view(['PUT', 'PATCH'])
def update_profile(request):
    if not request.user.is_authenticated:
        return Response({ "detail": "Uhhhh, I'm sorry, do I know you?", 'code': 'not_authenticated' }, status=status.HTTP_401_UNAUTHORIZED)
    partial = request.method == 'PUT'
    serializer = UpdateUserDataSerializer(request.user, data=request.data, partial=partial)
    serializer.is_valid(raise_exception=True)
    serializer.save()
    return Response(serializer.data, status=status.HTTP_200_OK)

@csrf_exempt
@api_view(['GET'])
def view_profile(request):
    if not request.user.is_authenticated:
        return Response({ "detail": "Uhhhh, I'm sorry, do I know you?", 'code': 'not_authenticated' }, status=status.HTTP_401_UNAUTHORIZED)
    return Response({
        "phone_number": request.user.phone_number,
        "role": request.user.role,
        "metadata": request.user.metadata,
        "email": request.user.email,
        "is_staff": request.user.is_staff,
        "is_superuser": request.user.is_superuser
    })



class UsersViewSet(ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAdminUser]
    