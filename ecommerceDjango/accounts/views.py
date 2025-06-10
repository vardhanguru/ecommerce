import json
import random
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth import authenticate, login, logout
from rest_framework.authtoken.models import Token
from django.utils import timezone
from accounts.models import CustomUser, EmailOTP
from rest_framework.authentication import TokenAuthentication
from rest_framework.exceptions import AuthenticationFailed

@csrf_exempt
def user_login(request):
    if request.method == 'OPTIONS':
        response = JsonResponse({}, status=200)
        response['Access-Control-Allow-Origin'] = 'http://127.0.0.1:3000'
        response['Access-Control-Allow-Credentials'] = 'true'
        response['Access-Control-Allow-Methods'] = 'GET, POST, OPTIONS'
        response['Access-Control-Allow-Headers'] = 'Content-Type, Authorization'
        return response
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            email_or_username = data.get('email_or_username')
            password = data.get('password')
            print(f"Login attempt for {email_or_username}")
            user = authenticate(request, username=email_or_username, password=password)
            if user is not None:
                if not user.is_email_verified:
                    print(f"User {email_or_username} email not verified")
                    return JsonResponse({'status': 'error', 'message': 'Email not verified'}, status=401)
                login(request, user)
                token, created = Token.objects.get_or_create(user=user)
                print(f"User {user.username} logged in, token: {token.key}")
                response = JsonResponse({
                    'status': 'success',
                    'token': token.key,
                    'redirect': 'http://127.0.0.1:3000/home.html'
                })
                response['Access-Control-Allow-Origin'] = 'http://127.0.0.1:3000'
                response['Access-Control-Allow-Credentials'] = 'true'
                return response
            print(f"Login failed for {email_or_username}")
            return JsonResponse({'status': 'error', 'message': 'Invalid credentials'}, status=401)
        except json.JSONDecodeError:
            print("Invalid JSON in login request")
            return JsonResponse({'status': 'error', 'message': 'Invalid JSON'}, status=400)
    return JsonResponse({'status': 'error', 'message': 'Invalid request'}, status=400)

@csrf_exempt
def get_user(request):
    if request.method == 'OPTIONS':
        response = JsonResponse({}, status=200)
        response['Access-Control-Allow-Origin'] = 'http://127.0.0.1:3000'
        response['Access-Control-Allow-Credentials'] = 'true'
        response['Access-Control-Allow-Methods'] = 'GET, POST, OPTIONS'
        response['Access-Control-Allow-Headers'] = 'Content-Type, Authorization'
        return response
    try:
        auth = TokenAuthentication().authenticate(request)
        if auth is None:
            print("No token provided for /account/user/")
            raise AuthenticationFailed('No token provided')
        user, _ = auth
        print(f"User {user.username} authenticated via token")
        response = JsonResponse({
            'status': 'success',
            'user': {
                'first_name': user.first_name,
                'last_name': user.last_name,
                'username': user.username,
                'email': user.email,
                'phone': user.phone
            }
        })
        response['Access-Control-Allow-Origin'] = 'http://127.0.0.1:3000'
        response['Access-Control-Allow-Credentials'] = 'true'
        return response
    except AuthenticationFailed as e:
        print(f"Authentication failed: {e}")
        response = JsonResponse({'status': 'error', 'message': 'Not authenticated'}, status=401)
        response['Access-Control-Allow-Origin'] = 'http://127.0.0.1:3000'
        response['Access-Control-Allow-Credentials'] = 'true'
        return response

@csrf_exempt
def logout(request):
    if request.method == 'OPTIONS':
        response = JsonResponse({}, status=200)
        response['Access-Control-Allow-Origin'] = 'http://127.0.0.1:3000'
        response['Access-Control-Allow-Credentials'] = 'true'
        response['Access-Control-Allow-Methods'] = 'GET, POST, OPTIONS'
        response['Access-Control-Allow-Headers'] = 'Content-Type, Authorization'
        return response
    if request.method == 'POST':
        try:
            auth = TokenAuthentication().authenticate(request)
            if auth is not None:
                user, token = auth
                print(f"User {user.username} logging out, deleting token {token.key}")
                token.delete()
                logout(request)
                response = JsonResponse({'status': 'success', 'message': 'Logout successful', 'redirect': 'http://127.0.0.1:3000/login.html'})
                response['Access-Control-Allow-Origin'] = 'http://127.0.0.1:3000'
                response['Access-Control-Allow-Credentials'] = 'true'
                return response
            print("No valid token for logout")
            return JsonResponse({'status': 'error', 'message': 'Not authenticated'}, status=401)
        except AuthenticationFailed:
            print("Authentication failed during logout")
            return JsonResponse({'status': 'error', 'message': 'Not authenticated'}, status=401)
    return JsonResponse({'status': 'error', 'message': 'Invalid request'}, status=400)

@csrf_exempt
def register(request):
    if request.method == 'OPTIONS':
        response = JsonResponse({}, status=200)
        response['Access-Control-Allow-Origin'] = 'http://127.0.0.1:3000'
        response['Access-Control-Allow-Credentials'] = 'true'
        response['Access-Control-Allow-Methods'] = 'GET, POST, OPTIONS'
        response['Access-Control-Allow-Headers'] = 'Content-Type, Authorization'
        return response
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            email = data.get('email')
            username = data.get('username')
            password = data.get('password')
            first_name = data.get('first_name')
            last_name = data.get('last_name')
            phone = data.get('phone')
            print(f"Registering user with email: {email}")
            try:
                user = CustomUser.objects.get(email=email)
                if not user.is_email_verified:
                    print(f"Email {email} not verified")
                    return JsonResponse({'status': 'error', 'message': 'Email not verified'}, status=400)
                user.username = username
                user.set_password(password)
                user.first_name = first_name
                user.last_name = last_name
                user.phone = phone
                user.save()
            except CustomUser.DoesNotExist:
                print(f"User with email {email} does not exist")
                return JsonResponse({'status': 'error', 'message': 'User does not exist'}, status=400)
            # Auto-login after registration
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                token, created = Token.objects.get_or_create(user=user)
                print(f"User {username} registered and logged in, token: {token.key}")
                response = JsonResponse({
                    'status': 'success',
                    'token': token.key,
                    'redirect': 'http://127.0.0.1:3000/home.html'
                })
                response['Access-Control-Allow-Origin'] = 'http://127.0.0.1:3000'
                response['Access-Control-Allow-Credentials'] = 'true'
                return response
            print(f"Authentication failed after registration for {username}")
            return JsonResponse({'status': 'success', 'redirect': 'http://127.0.0.1:3000/login.html'})
        except json.JSONDecodeError:
            print("Invalid JSON in register request")
            return JsonResponse({'status': 'error', 'message': 'Invalid JSON'}, status=400)
    return JsonResponse({'status': 'error', 'message': 'Invalid request'}, status=400)

@csrf_exempt
def generate_otp(request):
    if request.method == 'OPTIONS':
        response = JsonResponse({}, status=200)
        response['Access-Control-Allow-Origin'] = 'http://127.0.0.1:3000'
        response['Access-Control-Allow-Credentials'] = 'true'
        response['Access-Control-Allow-Methods'] = 'GET, POST, OPTIONS'
        response['Access-Control-Allow-Headers'] = 'Content-Type, Authorization'
        return response
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            email = data.get('email')
            user, created = CustomUser.objects.get_or_create(
                email=email,
                defaults={
                    'username': email.split('@')[0],
                    'password': 'default_temp_password'
                }
            )
            otp = str(random.randint(100000, 999999))
            EmailOTP.objects.create(
                user=user,
                otp=otp
            )
            print(f"OTP for {email} is {otp}")
            return JsonResponse({'status': 'success'})
        except json.JSONDecodeError:
            print("Invalid JSON in generate_otp request")
            return JsonResponse({'status': 'error', 'message': 'Invalid JSON'}, status=400)
    return JsonResponse({'status': 'error', 'message': 'Invalid request'}, status=400)

@csrf_exempt
def verify_otp(request):
    if request.method == 'OPTIONS':
        response = JsonResponse({}, status=200)
        response['Access-Control-Allow-Origin'] = 'http://127.0.0.1:3000'
        response['Access-Control-Allow-Credentials'] = 'true'
        response['Access-Control-Allow-Methods'] = 'GET, POST, OPTIONS'
        response['Access-Control-Allow-Headers'] = 'Content-Type, Authorization'
        return response
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            email = data.get('email')
            otp = data.get('otp')
            user = CustomUser.objects.get(email=email)
            otp_record = EmailOTP.objects.filter(
                user=user,
                otp=otp,
                is_verified=False
            ).latest('created_at')
            if (timezone.now() - otp_record.created_at).seconds > 60:
                print(f"OTP expired for {email}")
                return JsonResponse({'status': 'error', 'message': 'OTP is expired'}, status=400)
            otp_record.is_verified = True
            otp_record.save()
            user.is_email_verified = True
            user.save()
            print(f"OTP verified for {email}")
            return JsonResponse({'status': 'success'})
        except (CustomUser.DoesNotExist, EmailOTP.DoesNotExist):
            print(f"Invalid OTP for {email}")
            return JsonResponse({'status': 'error', 'message': 'Invalid OTP'}, status=400)
        except json.JSONDecodeError:
            print("Invalid JSON in verify_otp request")
            return JsonResponse({'status': 'error', 'message': 'Invalid JSON'}, status=400)
    return JsonResponse({'status': 'error', 'message': 'Invalid request'}, status=400)