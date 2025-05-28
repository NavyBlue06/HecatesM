from django.contrib import admin
from .models import MagicalItem


@admin.register(MagicalItem)
class MagicalItemAdmin(admin.ModelAdmin):
    list_display = ("name", "price", "sku")
