# shop/views.py
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from .models import Product, Cart, CartItem
import json

import logging

# Set up logging
logger = logging.getLogger(__name__)

@csrf_exempt
def home_products(request):
    if request.method == 'GET':
        try:
            products = Product.objects.all()  # Remove the limit to get all products
            if not products.exists():
                logger.warning("No products found in the database")
                return JsonResponse({'status': 'success', 'products': [], 'message': 'No products available'})
            
            products_data = [
                {
                    'id': product.id,
                    'name': product.name,
                    'price': float(product.price),
                    'image': product.image,
                    'description': product.description,
                    'category': product.category.name
                }
                for product in products
            ]
            logger.info(f"Successfully fetched {len(products_data)} products")
            return JsonResponse({'status': 'success', 'products': products_data})
        except Exception as e:
            logger.error(f"Error fetching products: {str(e)}")
            return JsonResponse({'status': 'error', 'message': str(e)}, status=500)
    return JsonResponse({'status': 'error', 'message': 'Method not allowed'}, status=405)

@csrf_exempt
@login_required
def get_or_create_cart(request):
    if request.method == 'GET':
        cart, created = Cart.objects.get_or_create(user=request.user)
        cart_items = [
            {
                'id': item.id,
                'product_id': item.product.id,
                'name': item.product.name,
                'price': float(item.product.price),
                'quantity': item.quantity,
                'image': item.product.image,
                'total': float(item.total_price)
            }
            for item in cart.items.all()
        ]
        return JsonResponse({
            'status': 'success',
            'cart_id': cart.id,
            'total_price': float(cart.total_price),
            'items': cart_items
        })
    return JsonResponse({'status': 'error'}, status=405)

@csrf_exempt
@login_required
def add_to_cart(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            product_id = data.get('product_id')
            quantity = data.get('quantity', 1)
            
            cart, created = Cart.objects.get_or_create(user=request.user)
            product = Product.objects.get(id=product_id)
            
            cart_item, created = CartItem.objects.get_or_create(
                cart=cart,
                product=product,
                defaults={'quantity': quantity}
            )
            
            if not created:
                cart_item.quantity += quantity
                cart_item.save()
                
            return JsonResponse({'status': 'success', 'message': 'Product added to cart'})
        except Product.DoesNotExist:
            return JsonResponse({'status': 'error', 'message': 'Product not found'}, status=404)
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=400)
    return JsonResponse({'status': 'error'}, status=405)

@csrf_exempt
@login_required
def remove_from_cart(request, item_id):
    if request.method == 'DELETE':
        try:
            cart_item = CartItem.objects.get(id=item_id, cart__user=request.user)
            cart_item.delete()
            return JsonResponse({'status': 'success', 'message': 'Item removed from cart'})
        except CartItem.DoesNotExist:
            return JsonResponse({'status': 'error', 'message': 'Item not found'}, status=404)
    return JsonResponse({'status': 'error'}, status=405)