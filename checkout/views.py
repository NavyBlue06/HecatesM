import json
import stripe
from decimal import Decimal

from django.shortcuts import render, get_object_or_404, redirect
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse, HttpResponseBadRequest
from django.conf import settings
from django.utils.timezone import now
from django.contrib.auth.decorators import login_required
from django.contrib import messages

from .forms import OrderForm
from .models import Order, OrderLineItem
from boxes.models import Product
from cart.cart import Cart

stripe.api_key = settings.STRIPE_SECRET_KEY

# --------------------
# Checkout View
# --------------------
def checkout(request):
    cart = Cart(request)

    if not cart.cart:
        messages.error(
            request, "Your cart is empty. Please add items before checking out."
        )
        return redirect("cart")

    if request.method == "POST":
        form = OrderForm(request.POST)
        if form.is_valid():
            # Store form data in session for later use
            request.session["order_data"] = {
                key: str(value) if isinstance(value, Decimal) else value
                for key, value in form.cleaned_data.items()
            }
            request.session["payment_intent_client_secret"] = request.POST.get(
                "client_secret"
            )
            return JsonResponse(
                {"client_secret": request.session.get("payment_intent_client_secret")}
            )
    else:
        form = OrderForm()

    # Safely convert total to Decimal
    total = Decimal(str(cart.get_total_price()))
    discount_amount = Decimal("0.00")
    promo_code = ""

    # --------------------
    # Check for first-time user discount
    # --------------------
    is_first_purchase = False
    if request.user.is_authenticated:
        previous_orders = Order.objects.filter(user=request.user).count()
        is_first_purchase = previous_orders == 0
    else:
        # For guests, use email from session if available
        order_data = request.session.get("order_data", {})
        email = order_data.get("email", "")
        if email:
            previous_orders = Order.objects.filter(email=email).count()
            is_first_purchase = previous_orders == 0

    # --------------------
    # Apply discounts
    # --------------------
    order_data = request.session.get("order_data", {})
    input_promo_code = order_data.get("promo_code", "").strip().upper()

    if is_first_purchase:
        promo_code = "FIRST10"
        discount_amount = round(total * Decimal("0.10"), 2)
        total -= discount_amount
        if input_promo_code == "MOON10":
            messages.info(
                request,
                "A 10% first-purchase discount has been applied automatically. The MOON10 code cannot be combined with this offer.",
            )
    elif input_promo_code == "MOON10":
        promo_code = "MOON10"
        discount_amount = round(total * Decimal("0.10"), 2)
        total -= discount_amount

    # Stripe minimum: ensure total is not 0
    if total <= 0:
        total = Decimal("0.01")

    total_in_cents = int(total * 100)

    # Safe cart data for Stripe metadata
    safe_cart = {k: {sk: str(sv) for sk, sv in v.items()} for k, v in cart.cart.items()}

    # Create Stripe payment intent
    intent = stripe.PaymentIntent.create(
        amount=total_in_cents,
        currency="eur",
        automatic_payment_methods={"enabled": True},
        metadata={
            "cart": json.dumps(safe_cart),
            "username": (
                request.user.username if request.user.is_authenticated else "guest"
            ),
            "promo_code": promo_code,
            "discount_amount": str(discount_amount),
        },
    )

    # Save needed values in session
    request.session["payment_intent_client_secret"] = intent.client_secret
    request.session["calculated_total"] = str(total)
    request.session["discount_amount"] = str(discount_amount)
    request.session["promo_code"] = promo_code if promo_code else ""

    return render(
        request,
        "checkout/checkout.html",
        {
            "form": form,
            "cart": cart,
            "stripe_public_key": settings.STRIPE_PUBLIC_KEY,
            "client_secret": intent.client_secret,
        },
    )

# --------------------
# Checkout Success View
# --------------------
def checkout_success(request, order_number):
    order = get_object_or_404(Order, order_number=order_number)
    cart = Cart(request)
    cart.clear()
    return render(request, "checkout/checkout_success.html", {"order": order})

# --------------------
# Fallback to retrieve order number if payment intent succeeded but confirm failed
# --------------------
@csrf_exempt
def get_order_number(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            pid = data.get("pid")
            order = Order.objects.get(stripe_pid=pid)
            return JsonResponse({"order_number": order.order_number})
        except (json.JSONDecodeError, KeyError):
            return JsonResponse({"error": "Invalid request data"}, status=400)
        except Order.DoesNotExist:
            return JsonResponse({"error": "Order not found"}, status=404)
    return HttpResponseBadRequest("This endpoint only accepts POST requests.")

# --------------------
# Confirm Payment View
# --------------------
@csrf_exempt
def confirm_payment(request):
    if request.method == "POST":
        data = json.loads(request.body)
        pid = data.get("pid")

        try:
            intent = stripe.PaymentIntent.retrieve(pid)
            if intent.status == "succeeded":
                order_data = request.session.get("order_data", {})
                cart = Cart(request)

                total = Decimal(request.session.get("calculated_total", "0.00"))
                discount_amount = Decimal(
                    request.session.get("discount_amount", "0.00")
                )
                promo_code = request.session.get("promo_code", "")

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
                    order_total=total + discount_amount,
                    promo_code=promo_code,
                    discount_amount=discount_amount,
                )

                for item_key, item_data in cart.cart.items():
                    try:
                        if item_data.get("product_type") == "box":
                            product_id = int(item_key.split("_")[1])
                            product = Product.objects.get(id=product_id)
                        elif item_data.get("product_type") == "magical":
                            product_id = int(item_key.split("_")[1])
                            from hecatemarket.models import MagicalItem

                            product = MagicalItem.objects.get(id=product_id)
                        else:
                            continue

                        OrderLineItem.objects.create(
                            order=order,
                            product=product,
                            quantity=item_data["quantity"],
                        )
                    except Exception as e:
                        print("Error adding item to order:", e)
                        continue

                order.update_total()
                order.save()
                # Clear session data after successful order creation

                request.session["order_data"] = {}
                request.session["payment_intent_client_secret"] = ""
                request.session["calculated_total"] = ""
                request.session["discount_amount"] = ""
                request.session["promo_code"] = ""

                return JsonResponse({"order_number": order.order_number})

            return JsonResponse({"error": "Payment not succeeded"}, status=400)

        except stripe.error.StripeError as e:
            return JsonResponse({"error": str(e)}, status=400)
        except Product.DoesNotExist:
            return JsonResponse({"error": "Product not found"}, status=404)
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)

    return JsonResponse({"error": "Invalid method"}, status=400)

# --------------------
# User Orders Views
# --------------------
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
