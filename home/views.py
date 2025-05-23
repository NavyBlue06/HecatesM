from django.shortcuts import render
from boxes.models import Product
from hecatemarket.models import MagicalItem
from services.models import (
    BirthChartRequest,
    WitchQuestion,
    RitualRequest,
    DreamSubmission,
    MediumContactRequest,
)

def index(request):
    return render(request, 'home/index.html')


def search_results(request):
    query = request.GET.get("q", "")

    products = Product.objects.filter(name__icontains=query) | Product.objects.filter(
        description__icontains=query
    )
    magical_items = MagicalItem.objects.filter(
        name__icontains=query
    ) | MagicalItem.objects.filter(description__icontains=query)

    # Only search services by keyword match, not full querysets
    services = []
    if "birth" in query.lower():
        services.append("🌕 Birth Chart Reading")
    if "witch" in query.lower():
        services.append("🧙 Ask a Witch")
    if "ritual" in query.lower():
        services.append("🕯️ Ritual Request")
    if "dream" in query.lower():
        services.append("🌙 Dream Interpretation")
    if "medium" in query.lower():
        services.append("👻 Medium Contact")

    return render(
        request,
        "home/search_results.html",
        {
            "query": query,
            "products": products,
            "magical_items": magical_items,
            "services": services,
        },
    )
