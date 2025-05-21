from django.contrib import admin
from .models import Product


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ("name", "price", "category", "is_available")
    search_fields = ("name", "category")
    list_filter = ("is_available", "category")
