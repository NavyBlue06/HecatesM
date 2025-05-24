from django.urls import path
from . import views

urlpatterns = [
    path("", views.market_landing, name="market_landing"),
    path("items/", views.market_items, name="market_items"),
    path("add_to_cart/<int:item_id>/", views.add_to_cart_item, name="add_to_cart_item"),
]
