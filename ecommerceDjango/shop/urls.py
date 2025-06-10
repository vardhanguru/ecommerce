from django.urls import path
from shop.views import products, product_detail, checkout, cart, cart_add,create_payment_intent

urlpatterns = [
    path('products/', products, name='products'),
    path('product/<slug:slug>/', product_detail, name='product_detail'),
    path('cart/', cart, name='cart'),
    path('cart/add/', cart_add, name='cart_add'),
    path('checkout/', checkout),
    path('create-payment-intent/', create_payment_intent),
]