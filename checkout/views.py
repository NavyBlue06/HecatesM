import json
import stripe
from decimal import Decimal

from django.shortcuts import render, get_object_or_404, redirect
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from django.conf import settings
from django.utils.timezone import now
from django.contrib.auth.decorators import login_required
from django.contrib import messages

from .forms import OrderForm
from .models import Order, OrderLineItem
from boxes.models import Product
from cart.cart import Cart

stripe.api_key = settings.STRIPE_SECRET_KEY


def checkout(request):
    cart = Cart(request)

    if request.method == 'POST':
        form = OrderForm(request.POST)
        if form.is_valid():
            request.session['order_data'] = {
                key: str(value) if isinstance(value, Decimal) else value
                for key, value in form.cleaned_data.items()
            }
            request.session['payment_intent_client_secret'] = request.POST.get('client_secret')
            return JsonResponse({
                'client_secret': request.session.get('payment_intent_client_secret')
            })
    else:
        form = OrderForm()

    total = int(cart.get_total_price() * 100)

    safe_cart = {
        k: {sk: str(sv) for sk, sv in v.items()} for k, v in cart.cart.items()
    }

    intent = stripe.PaymentIntent.create(
        amount=total,
        currency='eur',
        metadata={
            'cart': json.dumps(safe_cart),
            'username': request.user.username if request.user.is_authenticated else 'guest'
        }
    )

    request.session['payment_intent_client_secret'] = intent.client_secret

    return render(request, 'checkout/checkout.html', {
        'form': form,
        'cart': cart,
        'stripe_public_key': settings.STRIPE_PUBLIC_KEY,
        'client_secret': intent.client_secret
    })


def checkout_success(request, order_number):
    order = get_object_or_404(Order, order_number=order_number)
    cart = Cart(request)
    cart.clear()
    return render(request, 'checkout/checkout_success.html', {'order': order})


@csrf_exempt
def get_order_number(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        pid = data.get('pid')
        try:
            order = Order.objects.get(stripe_pid=pid)
            return JsonResponse({'order_number': order.order_number})
        except Order.DoesNotExist:
            return JsonResponse({'error': 'Order not found'}, status=404)


@csrf_exempt
def confirm_payment(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        pid = data.get('pid')

        try:
            intent = stripe.PaymentIntent.retrieve(pid)
            if intent.status == "succeeded":
                order_data = request.session.get('order_data', {})
                cart = Cart(request)
                total = cart.get_total_price()

                order = Order.objects.create(
                    user=request.user if request.user.is_authenticated else None,
                    full_name=order_data.get("full_name", ""),
                    email=order_data.get("email", ""),
                    phone_number=order_data.get("phone_number", ""),
                    street_address1=order_data.get("street_address1", ""),
                    street_address2=order_data.get("street_address2", ""),
                    town_or_city=order_data.get("town_or_city", ""),
                    postcode=order_data.get("postcode", ""),
                    country=order_data.get("country", ""),
                    county=order_data.get("county", ""),
                    stripe_pid=pid,
                    order_total=total,
                )

                for item_id, item_data in cart.cart.items():
                    product = Product.objects.get(id=item_id)
                    OrderLineItem.objects.create(
                        order=order,
                        product=product,
                        quantity=item_data['quantity'],
                    )

                order.update_total()
                request.session['order_data'] = {}
                request.session["payment_intent_client_secret"] = ""
                return JsonResponse({'order_number': order.order_number})

            return JsonResponse({'error': 'Payment not succeeded'}, status=400)

        except stripe.error.StripeError as e:
            return JsonResponse({'error': str(e)}, status=400)
        except Product.DoesNotExist:
            return JsonResponse({'error': 'Product not found'}, status=404)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)

    return JsonResponse({'error': 'Invalid method'}, status=400)


# -------------------
#  USER ORDER VIEWS
# -------------------


@login_required
def my_orders(request):
    orders = Order.objects.filter(user=request.user).order_by("-date")
    return render(request, "checkout/my_orders.html", {"orders": orders})


@login_required
def edit_order(request, order_id):
    order = get_object_or_404(Order, id=order_id, user=request.user)
    time_diff = now() - order.date

    if time_diff.total_seconds() > 43200:
        messages.error(request, "You can only edit orders within 12 hours.")
        return redirect("my_orders")

    if request.method == "POST":
        form = OrderForm(request.POST, instance=order)
        if form.is_valid():
            form.save()
            messages.success(request, "Order updated successfully.")
            return redirect("my_orders")
    else:
        form = OrderForm(instance=order)

    return render(request, "checkout/edit_order.html", {"form": form, "order": order})


@login_required
def delete_order(request, order_id):
    order = get_object_or_404(Order, id=order_id, user=request.user)
    time_diff = now() - order.date

    if time_diff.total_seconds() > 43200:
        messages.error(request, "You can only delete orders within 12 hours.")
        return redirect("my_orders")

    if request.method == "POST":
        order.delete()
        messages.success(request, "Order deleted.")
        return redirect("my_orders")

    return render(request, "checkout/confirm_delete.html", {"order": order})
