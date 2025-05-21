from django.urls import path
from . import views

urlpatterns = [
    path('', views.services_home, name='services_home'),
    path('add-service-to-cart/<str:service_type>/<int:object_id>/', views.add_service_to_cart, name='add_service_to_cart'),
]
