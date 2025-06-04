
from django.urls import path
from . import views

urlpatterns = [
    path('register/', views.register, name='register'),
    path('generate-otp/', views.generate_otp, name='generate_otp'),
    path('verify-otp/', views.verify_otp, name='verify_otp'),
    path('login/', views.user_login, name='login'),
    path('user/', views.get_user, name='get_user'),
    path('logout/', views.user_logout, name='logout'),
]
