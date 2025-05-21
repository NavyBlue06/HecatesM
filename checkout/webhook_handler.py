from django.http import HttpResponse
import json
from .models import Order, OrderLineItem
from boxes.models import Product
from decimal import Decimal

class StripeWH_Handler:
    def __init__(self, request):
        self.request = request

    def handle_event(self, event):
        return HttpResponse(content=f'Unhandled event: {event["type"]}', status=200)

    def handle_payment_intent_failed(self, event):
        return HttpResponse(content=f'Payment failed: {event["type"]}', status=200)

    def handle_payment_intent_succeeded(self, event):
        intent = event.data.object
        pid = intent.id

        order_data = self.request.session.get('order_data')
        cart = self.request.session.get('cart', {})

        if not order_data:
            return HttpResponse("No order data", status=400)

        order = Order(
            full_name=order_data['full_name'],
            email=order_data['email'],
            phone_number=order_data['phone_number'],
            country=order_data['country'],
            postcode=order_data['postcode'],
            town_or_city=order_data['town_or_city'],
            street_address1=order_data['street_address1'],
            street_address2=order_data['street_address2'],
            county=order_data['county'],
            original_cart=json.dumps(cart),
            stripe_pid=pid,
        )
        order.save()

        for item_id, item in cart.items():
            product = Product.objects.get(id=item['product_id'])
            OrderLineItem.objects.create(
                order=order,
                product=product,
                quantity=item['quantity']
            )

        return HttpResponse(content=f'Webhook handled: {event["type"]}', status=200)

