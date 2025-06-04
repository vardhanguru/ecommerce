# shop/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('products/', views.home_products, name='home_products'),
    path('cart/', views.get_or_create_cart, name='get_cart'),
    path('cart/add/', views.add_to_cart, name='add_to_cart'),
    path('cart/remove/<int:item_id>/', views.remove_from_cart, name='remove_from_cart'),
]