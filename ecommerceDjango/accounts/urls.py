from django.urls import path
from accounts.views import user_login, get_user, logout, register, generate_otp, verify_otp

urlpatterns = [
    path('login/', user_login, name='user_login'),
    path('user/', get_user, name='get_user'),
    path('logout/', logout, name='logout'),
    path('register/', register, name='register'),
    path('generate_otp/', generate_otp, name='generate_otp'),
    path('verify_otp/', verify_otp, name='verify_otp'),
]