import stripe
from django.conf import settings
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from rest_framework.authentication import TokenAuthentication
from rest_framework.exceptions import AuthenticationFailed
from shop.models import Product, Cart, CartItem, Category, Order, OrderItem
import json

@csrf_exempt
def products(request):
    """
    Fetch all products for display on the home page.
    Requires token authentication.
    """

    if request.method == 'GET':
        try:
            auth = TokenAuthentication().authenticate(request)
            if auth is None:
                print("No token provided for /shop/products/")
                return JsonResponse({'status': 'error', 'message': 'Not authenticated'}, status=401)
            products = Product.objects.select_related('category').all()
            print(f"Returning {products.count()} products")
            response = JsonResponse({
                'status': 'success',
                'products': [{
                    'id': p.id,
                    'name': p.name,
                    'slug': p.slug,
                    'description': p.description,
                    'price': float(p.price),
                    'category': p.category.name,
                    'image': p.image,
                    'stock': p.stock,
                    'created_at': p.created_at.isoformat()
                } for p in products]
            })
            response['Access-Control-Allow-Origin'] = 'http://127.0.0.1:3000'
            response['Access-Control-Allow-Credentials'] = 'true'
            return response
        except AuthenticationFailed:
            print("Authentication failed for /shop/products/")
            return JsonResponse({'status': 'error', 'message': 'Not authenticated'}, status=401)
    return JsonResponse({'status': 'error', 'message': 'Invalid request'}, status=400)

@csrf_exempt
def product_detail(request, slug):
    """
    Fetch details for a single product by slug.
    Requires token authentication.
    """

    if request.method == 'GET':
        try:
            auth = TokenAuthentication().authenticate(request)
            if auth is None:
                print("No token provided for /shop/product/<slug>/")
                return JsonResponse({'status': 'error', 'message': 'Not authenticated'}, status=401)
            product = Product.objects.select_related('category').get(slug=slug)
            print(f"Returning product: {product.name}")
            response = JsonResponse({
                'status': 'success',
                'product': {
                    'id': product.id,
                    'name': product.name,
                    'slug': product.slug,
                    'description': product.description,
                    'price': float(product.price),
                    'category': product.category.name,
                    'image': product.image,
                    'stock': product.stock,
                    'created_at': product.created_at.isoformat()
                }
            })
            response['Access-Control-Allow-Origin'] = 'http://127.0.0.1:3000'
            response['Access-Control-Allow-Credentials'] = 'true'
            return response
        except Product.DoesNotExist:
            print(f"Product with slug {slug} not found")
            return JsonResponse({'status': 'error', 'message': 'Product not found'}, status=404)
        except AuthenticationFailed:
            print("Authentication failed for /shop/product/<slug>/")
            return JsonResponse({'status': 'error', 'message': 'Not authenticated'}, status=401)
    return JsonResponse({'status': 'error', 'message': 'Invalid request'}, status=400)

@csrf_exempt
def cart_add(request):
    """
    Add a product to the user's cart.
    Requires token authentication.
    """
    if request.method == 'OPTIONS':
        response = JsonResponse({}, status=200)
        response['Access-Control-Allow-Origin'] = 'http://127.0.0.1:3000'
        response['Access-Control-Allow-Credentials'] = 'true'
        response['Access-Control-Allow-Methods'] = 'POST, OPTIONS'
        response['Access-Control-Allow-Headers'] = 'Content-Type, Authorization'
        return response
    if request.method == 'POST':
        try:
            auth = TokenAuthentication().authenticate(request)
            if auth is None:
                print("No token provided for /shop/cart/add/")
                return JsonResponse({'status': 'error', 'message': 'Not authenticated'}, status=401)
            user, _ = auth
            data = json.loads(request.body)
            product_id = data.get('product_id')
            quantity = data.get('quantity', 1)
            try:
                product = Product.objects.get(id=product_id)
                if product.stock < quantity:
                    print(f"Insufficient stock for product {product.name}")
                    return JsonResponse({'status': 'error', 'message': 'Insufficient stock'}, status=400)
                cart, created = Cart.objects.get_or_create(user=user)
                cart_item, created = CartItem.objects.get_or_create(cart=cart, product=product)
                if not created:
                    cart_item.quantity += quantity
                else:
                    cart_item.quantity = quantity
                cart_item.save()
                cart.updated_at = cart.updated_at  # Trigger update
                cart.save()
                print(f"Added {quantity} of {product.name} to cart for {user.username}")
                return JsonResponse({'status': 'success', 'message': 'Product added to cart'})
            except Product.DoesNotExist:
                print(f"Product {product_id} not found")
                return JsonResponse({'status': 'error', 'message': 'Product not found'}, status=404)
        except json.JSONDecodeError:
            print("Invalid JSON in cart_add request")
            return JsonResponse({'status': 'error', 'message': 'Invalid JSON'}, status=400)
        except AuthenticationFailed:
            print("Authentication failed for /shop/cart/add/")
            return JsonResponse({'status': 'error', 'message': 'Not authenticated'}, status=401)
    return JsonResponse({'status': 'error', 'message': 'Invalid request'}, status=400)

@csrf_exempt
def cart(request):
    """
    Fetch the user's cart with all items.
    Requires token authentication.
    """

    if request.method == 'GET':
        try:
            auth = TokenAuthentication().authenticate(request)
            if auth is None:
                print("No token provided for /shop/cart/")
                return JsonResponse({'status': 'error', 'message': 'Not authenticated'}, status=401)
            user, _ = auth
            cart, created = Cart.objects.get_or_create(user=user)
            items = CartItem.objects.filter(cart=cart).select_related('product', 'product__category')
            print(f"Returning cart for user {user.username} with {items.count()} items")
            response = JsonResponse({
                'status': 'success',
                'items': [{
                    'id': item.id,
                    'product_id': item.product.id,
                    'name': item.product.name,
                    'slug': item.product.slug,
                    'price': float(item.product.price),
                    'image': item.product.image,
                    'quantity': item.quantity,
                    'total': float(item.quantity * item.product.price)
                } for item in items],
                'total_price': float(sum(item.quantity * item.product.price for item in items))
            })
            response['Access-Control-Allow-Origin'] = 'http://127.0.0.1:3000'
            response['Access-Control-Allow-Credentials'] = 'true'
            return response
        except AuthenticationFailed:
            print("Authentication failed for /shop/cart/")
            return JsonResponse({'status': 'error', 'message': 'Not authenticated'}, status=401)
    return JsonResponse({'status': 'error', 'message': 'Invalid request'}, status=400)


# shop/views.py
@csrf_exempt
def checkout(request):
    """
    Place an order from the user's current cart.
    """
    if request.method == 'POST':
        try:
            auth = TokenAuthentication().authenticate(request)
            if auth is None:
                return JsonResponse({'status': 'error', 'message': 'Not authenticated'}, status=401)
            user, _ = auth
            cart = Cart.objects.get(user=user)
            cart_items = CartItem.objects.filter(cart=cart)

            if not cart_items.exists():
                return JsonResponse({'status': 'error', 'message': 'Cart is empty'}, status=400)

            total_amount = sum(item.quantity * item.product.price for item in cart_items)
            order = Order.objects.create(user=user, total_amount=total_amount)

            for item in cart_items:
                OrderItem.objects.create(
                    order=order,
                    product=item.product,
                    quantity=item.quantity,
                    price=item.product.price
                )

            # Clear cart
            cart_items.delete()

            return JsonResponse({'status': 'success', 'message': 'Order placed', 'order_id': order.id})
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=400)

stripe.api_key = settings.STRIPE_SECRET_KEY
# stripe.api_key = settings.STRIPE_PUBLISHABLE_KEY  # Set your secret key in settings.py

@csrf_exempt
def cart(request):
    if request.method == 'GET':
        try:
            auth = TokenAuthentication().authenticate(request)
            if auth is None:
                return JsonResponse({'status': 'error', 'message': 'Not authenticated'}, status=401)
            user, _ = auth
            cart, _ = Cart.objects.get_or_create(user=user)
            items = CartItem.objects.filter(cart=cart).select_related('product')
            return JsonResponse({
                'status': 'success',
                'items': [{
                    'id': item.id,
                    'product_id': item.product.id,
                    'name': item.product.name,
                    'slug': item.product.slug,
                    'price': float(item.product.price),
                    'image': item.product.image,
                    'quantity': item.quantity,
                    'total': float(item.quantity * item.product.price)
                } for item in items],
                'total_price': float(sum(item.quantity * item.product.price for item in items))
            })
        except AuthenticationFailed:
            return JsonResponse({'status': 'error', 'message': 'Not authenticated'}, status=401)
    return JsonResponse({'status': 'error', 'message': 'Invalid request'}, status=400)


@csrf_exempt
def create_payment_intent(request):
    if request.method == 'POST':
        try:
            auth = TokenAuthentication().authenticate(request)
            if auth is None:
                return JsonResponse({'status': 'error', 'message': 'Not authenticated'}, status=401)
            user, _ = auth
            data = json.loads(request.body)
            amount = data.get('amount')
            if amount is None or amount <= 0:
                return JsonResponse({'status': 'error', 'message': 'Invalid amount'}, status=400)

            # Optionally, verify cart total matches amount on server side here

            intent = stripe.PaymentIntent.create(
                amount=int(amount),  # amount in cents
                currency='usd',
                metadata={'user_id': user.id}
            )
            return JsonResponse({'status': 'success', 'client_secret': intent.client_secret})
        except json.JSONDecodeError:
            return JsonResponse({'status': 'error', 'message': 'Invalid JSON'}, status=400)
        except AuthenticationFailed:
            return JsonResponse({'status': 'error', 'message': 'Not authenticated'}, status=401)
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=500)
    return JsonResponse({'status': 'error', 'message': 'Invalid request'}, status=400)