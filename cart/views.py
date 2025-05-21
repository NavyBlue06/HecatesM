from django.shortcuts import redirect, get_object_or_404
from boxes.models import Product
from django.shortcuts import render
from .cart import Cart

def cart_detail(request):
    cart = Cart(request)
    return render(request, 'cart/cart_detail.html', {'cart': cart})

# add to cart
def add_to_cart(request, product_id):
    cart = Cart(request)
    product = get_object_or_404(Product, id=product_id)
    cart.add(product=product)
    return redirect('cart')

# remove from cart
def remove_from_cart(request, key):
    cart = Cart(request)
    if key in cart.cart:
        del cart.cart[key]
        cart.save()
    return redirect('cart')