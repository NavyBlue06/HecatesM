from django.urls import path
from . import views, webhook_view

urlpatterns = [
    path('', views.checkout, name='checkout'),
    path('checkout-success/<order_number>/', views.checkout_success, name='checkout_success'),
    path('webhook/', webhook_view.stripe_webhook, name='stripe_webhook'),
    path('get_order_number/', views.get_order_number, name='get_order_number'),
    path('confirm_payment/', views.confirm_payment, name='confirm_payment'),
]
