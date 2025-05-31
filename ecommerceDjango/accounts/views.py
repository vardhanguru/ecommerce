from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth import authenticate, login, logout
from .models import CustomUser, EmailOTP
import random
import json

@csrf_exempt
def register(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        email = data.get('email')
        
        try:
            user = CustomUser.objects.get(email=email)
            if not user.is_email_verified:
                return JsonResponse({'status': 'error', 'message': 'Email not verified'})
                
            # Update user details
            user.username = data.get('username')
            user.set_password(data.get('password'))
            user.first_name = data.get('first_name')
            user.last_name = data.get('last_name')
            user.phone = data.get('phone')
            user.save()
            return JsonResponse({'status': 'success'})
        except CustomUser.DoesNotExist:
            return JsonResponse({'status': 'error', 'message': 'Verify email first'})

@csrf_exempt
def generate_otp(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        email = data.get('email')
        
        # Create user if doesn't exist
        user, created = CustomUser.objects.get_or_create(
            email=email,
            defaults={
                'username': email.split('@')[0],
                'password': 'temporary_password_123'  # Will be set properly later
            }
        )
        
        # Generate 6-digit OTP
        otp = str(random.randint(100000, 999999))
        
        # Save OTP to database
        EmailOTP.objects.create(
            user=user,
            otp=otp
        )
        
        # Print OTP to console for development
        print(f"OTP for {email}: {otp}")
        
        return JsonResponse({'status': 'success'})

@csrf_exempt
def verify_otp(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        email = data.get('email')
        otp = data.get('otp')
        
        try:
            user = CustomUser.objects.get(email=email)
            otp_record = EmailOTP.objects.filter(
                user=user, 
                otp=otp,
                is_verified=False
            ).latest('created_at')
        except (CustomUser.DoesNotExist, EmailOTP.DoesNotExist):
            return JsonResponse({'status': 'error', 'message': 'Invalid OTP'})
        
        # Check if OTP is expired (5 minutes)
        from django.utils import timezone
        if (timezone.now() - otp_record.created_at).seconds > 300:
            return JsonResponse({'status': 'error', 'message': 'OTP expired'})
        
        # Mark OTP as verified
        otp_record.is_verified = True
        otp_record.save()
        
        # Mark email as verified
        user.is_email_verified = True
        user.save()
        
        return JsonResponse({'status': 'success'})

@csrf_exempt
def user_login(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        email_or_username = data.get('email_or_username')
        password = data.get('password')
        
        # Authenticate via email or username
        user = authenticate(
            request, 
            username=email_or_username, 
            password=password
        )
        
        if user is not None:
            if not user.is_email_verified:
                return JsonResponse({'status': 'error', 'message': 'Email not verified'})
                
            login(request, user)
            return JsonResponse({'status': 'success', 'redirect': '/home'})
        else:
            return JsonResponse({'status': 'error', 'message': 'Invalid credentials'})

@csrf_exempt
def get_user(request):
    if request.method == 'GET':
        if request.user.is_authenticated:
            return JsonResponse({
                'status': 'success',
                'user': {
                    'first_name': request.user.first_name,
                    'last_name': request.user.last_name,
                    'username': request.user.username,
                    'email': request.user.email,
                    'phone': request.user.phone
                }
            })
        else:
            return JsonResponse({'status': 'error', 'message': 'Not authenticated'}, status=401)

@csrf_exempt
def user_logout(request):
    if request.method == 'POST':
        print(request.POST)
        logout(request)
        return JsonResponse({'status': 'success'})