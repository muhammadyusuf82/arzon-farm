from django.urls import path
from authorization.views import *

urlpatterns = [
    path('begin-validation/<str:phone_number>', begin_validation),
    path('validate-phone-number/<str:phone_number>/<str:code>', validate_phone_number),
    path('create-user-via-key/<str:phone_number>/<str:user_create_key>', create_user_via_key),
    path('view-profile/', view_profile),
    path('update-profile/', update_profile),
    path('update-password-request/', update_password_request),
    path('update-password/<str:code>/<str:new_password>', update_password),
]