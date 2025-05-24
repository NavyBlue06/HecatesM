from django.shortcuts import render, get_object_or_404
from hecatemarket.models import MagicalItem # correct name of model Navahlicious!
from cart.cart import Cart
from django.contrib import messages


def market_landing(request):
    return render(request, 'hecatemarket/market_landing.html')


def market_items(request):
    items = MagicalItem.objects.filter(is_available=True)
    return render(request, 'hecatemarket/market_items.html', {'items': items})


def add_to_cart_item(request, item_id):
    item = get_object_or_404(MagicalItem, pk=item_id)
    cart = Cart(request)
    cart.add(product=item)
    messages.success(request, f"{item.name} was added to your cart.")
    return redirect("market_items")
