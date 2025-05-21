from django.shortcuts import render
from .models import Product


def all_products(request):
    products = Product.objects.filter(is_available=True)
    boxes = products.filter(category__icontains="box")
    items = products.exclude(category__icontains="box")

    return render(
        request,
        "boxes/all_products.html",
        {
            "boxes": boxes,
            "items": items,
        },
    )
