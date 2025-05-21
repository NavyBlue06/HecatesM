from decimal import Decimal
from django.conf import settings
from boxes.models import Product  # still needed in case I'm adding physical products

class Cart:
    def __init__(self, request):
        self.session = request.session
        cart = self.session.get(settings.CART_SESSION_ID)
        if not cart:
            cart = self.session[settings.CART_SESSION_ID] = {}
        self.cart = cart

    def add(self, product, quantity=1):
        product_id = str(product.id)

        # Convert Decimal price to string before storing in session
        price = product.price
        if isinstance(price, Decimal):
            price = str(price)

        if product_id not in self.cart:
            self.cart[product_id] = {
                'quantity': 0,
                'price': price,  # stored safely as string
                'product_id': product.id,
            }

        self.cart[product_id]['quantity'] += quantity
        self.save()

    def remove(self, item_key):
        if item_key in self.cart:
            del self.cart[item_key]
            self.save()

    def save(self):
        self.session.modified = True

    def __iter__(self):
        cart = self.cart.copy()
        for key, item in cart.items():
            if 'product_id' in item:
                try:
                    product = Product.objects.get(id=item['product_id'])
                    item['name'] = product.name
                    price = Decimal(item['price'])  # convert back to Decimal for math
                    item['price'] = float(price)  # convert to float for JSON-safe output
                    item['quantity'] = item['quantity']
                    item['total_price'] = float(price * item['quantity'])
                    item['type'] = 'product'
                    item['key'] = key
                    yield item
                except Product.DoesNotExist:
                    continue

            elif key.startswith('service-') or 'service_type' in item:
                item['name'] = item.get('service_type', 'Unknown Service')
                price = Decimal(str(item.get('price', 0)))
                item['price'] = float(price)
                item['quantity'] = 1
                item['total_price'] = float(price)
                item['type'] = 'service'
                item['key'] = key
                yield item

    def get_total_price(self):
        total = Decimal('0.00')
        for item in self:
            total += Decimal(str(item['total_price']))
        return float(total)

    def clear(self):
        self.session[settings.CART_SESSION_ID] = {}
        self.save()
