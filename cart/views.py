from django.shortcuts import redirect, get_object_or_404, render
from boxes.models import Product
from hecatemarket.models import MagicalItem
from django.contrib import messages
from .cart import Cart

def cart_detail(request):
    cart = Cart(request)
    cart_items = []

    for key, item in cart.cart.items():
        try:
            product_type = item.get("product_type", "box")
            quantity = item.get("quantity", 1)
            price = float(item.get("price", 0))

            if product_type == "magical":
                item_id = int(key.split("_")[1])
                product_obj = MagicalItem.objects.get(id=item_id)
            else:
                item_id = int(key.split("_")[1])
                product_obj = Product.objects.get(id=item_id)

            cart_items.append(
                {
                    "key": key,
                    "product": product_obj,
                    "quantity": quantity,
                    "price": price,
                    "total_price": round(price * quantity, 2),
                }
            )

        except (
            KeyError,
            IndexError,
            ValueError,
            Product.DoesNotExist,
            MagicalItem.DoesNotExist,
        ):
            continue  # skip broken cart entries

    return render(
        request,
        "cart/cart_detail.html",
        {
            "cart_items": cart_items,
            "total": cart.get_total_price(),
        },
    )

def add_to_cart(request, product_id):
    cart = Cart(request)
    product = get_object_or_404(Product, id=product_id)
    key = f"box_{product.id}"  # distinguish it
    cart.add(product=product, product_type="box", key=key)
    messages.success(request, f"{product.name} was added to your cart.")
    return redirect("all_boxes")

def remove_from_cart(request, key):
    cart = Cart(request)
    if key in cart.cart:
        del cart.cart[key]
        cart.save()
        messages.success(request, "Item removed from cart.")
    return redirect('cart')
