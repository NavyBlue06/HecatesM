from django.urls import path
from . import views

urlpatterns = [
    path('', views.market_landing, name='market_landing'),
    path('items/', views.market_items, name='market_items'), # magical items
]
