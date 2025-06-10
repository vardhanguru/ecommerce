from django.contrib import admin
from django.urls import path, include
# from accounts.views import serve_login, serve_home

urlpatterns = [
    path('admin/', admin.site.urls),
    path('account/', include('accounts.urls')),
    path('shop/', include('shop.urls')),
    
    # path('login/', serve_login, name='serve_login'),
    # path('home/', serve_home, name='serve_home'),
    # path('login/', serve_login, name='serve_login'),
]