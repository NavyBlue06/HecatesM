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
                "name": name if name else product.name,
                "price": str(price if price is not None else product.price),
            }

        if override_quantity:
            self.cart[product_id]["quantity"] = quantity
        else:
            self.cart[product_id]["quantity"] += quantity

        self.save()

    def save(self):
        self.session[settings.CART_SESSION_ID] = self.cart
        self.session.modified = True

    def remove(self, product_id):
        if product_id in self.cart:
            del self.cart[product_id]
            self.save()

    def clear(self):
        self.session[settings.CART_SESSION_ID] = {}
        self.session.modified = True

    def __iter__(self):
        for item_key, item in self.cart.items():
            product = None
            if item["product_type"] == "box":
                try:
                    product = Product.objects.get(id=int(item_key.split("_")[1]))
                except (Product.DoesNotExist, IndexError, ValueError):
                    continue
            elif item["product_type"] == "magical":
                try:
                    product = MagicalItem.objects.get(id=int(item_key.split("_")[1]))
                except (MagicalItem.DoesNotExist, IndexError, ValueError):
                    continue

            if product:
                item["product"] = product
                item["total_price"] = Decimal(item["price"]) * item["quantity"]
                yield item

    def __len__(self):
        return sum(item["quantity"] for item in self.cart.values())

    def get_total_price(self):
        return sum(
            Decimal(item["price"]) * item["quantity"] for item in self.cart.values()
        )
