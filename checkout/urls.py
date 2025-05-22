from django.urls import path
from . import views, webhook_view

urlpatterns = [
    path("", views.checkout, name="checkout"),
    path(
        "checkout-success/<order_number>/",
        views.checkout_success,
        name="checkout_success",
    ),
    path("webhook/", webhook_view.stripe_webhook, name="stripe_webhook"),
    path("get_order_number/", views.get_order_number, name="get_order_number"),
    path("confirm_payment/", views.confirm_payment, name="confirm_payment"),
    path("my-orders/", views.my_orders, name="my_orders"),
    path("edit-order/<int:order_id>/", views.edit_order, name="edit_order"),
    path("delete-order/<int:order_id>/", views.delete_order, name="delete_order"),
]
