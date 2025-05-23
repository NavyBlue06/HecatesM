from .cart import Cart

def cart_context(request):
    cart_obj = Cart(request)
    cart_items = []

    for key, item in cart_obj.cart.items():
        total_price = float(item.get("price", 0)) * int(item.get("quantity", 1))
        cart_items.append(
            {
                "key": key,
                "name": item.get("name", "Unknown Service"),
                "price": item.get("price", 0),
                "quantity": item.get("quantity", 1),
                "type": item.get("type", "unknown"),
                "total_price": total_price,
            }
        )

    return {"cart": cart_items, "cart_total": cart_obj.get_total_price()}
