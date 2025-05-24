from decimal import Decimal
from django.conf import settings
from boxes.models import Product
from hecatemarket.models import MagicalItem


class Cart:
    def __init__(self, request):
        self.session = request.session
        cart = self.session.get(settings.CART_SESSION_ID)
        if not cart:
            cart = self.session[settings.CART_SESSION_ID] = {}
        self.cart = cart

    def add(
        self,
        product=None,
        quantity=1,
        override_quantity=False,
        key=None,
        product_type="box",
        name=None,
        price=None,
    ):
        product_id = key if key else str(product.id)

        if product_id not in self.cart:
            self.cart[product_id] = {
                "quantity": 0,
                "product_type": product_type,
                "price": str(price if price is not None else product.price),
                "name": name if name else (product.name if product else "Unnamed"),
            }

        if override_quantity:
            self.cart[product_id]["quantity"] = quantity
        else:
            self.cart[product_id]["quantity"] += quantity

        self.save()

    def remove(self, item_key):
        if item_key in self.cart:
            del self.cart[item_key]
            self.save()

    def save(self):
        self.session.modified = True

    def __iter__(self):
        for key, item in self.cart.items():
            item_data = item.copy()
            price = Decimal(item_data["price"])

            if item_data.get("product_type") == "box":
                try:
                    item_data["product"] = Product.objects.get(name=item_data["name"])
                except Product.DoesNotExist:
                    continue

            elif item_data.get("product_type") == "magical":
                try:
                    item_data["product"] = MagicalItem.objects.get(
                        name=item_data["name"]
                    )
                except MagicalItem.DoesNotExist:
                    continue

            elif item_data.get("product_type") == "service":
                item_data["product"] = None

            item_data["price"] = float(price)
            item_data["total_price"] = float(price * item_data["quantity"])
            item_data["key"] = key
            yield item_data

    def get_total_price(self):
        total = Decimal("0.00")
        for item in self:
            total += Decimal(str(item["total_price"]))
        return float(total)

    def clear(self):
        self.session[settings.CART_SESSION_ID] = {}
        self.save()
