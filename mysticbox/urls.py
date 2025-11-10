"""
URL configuration for mysticbox project.
"""

from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from checkout import webhook_view

urlpatterns = [
    path("admin/", admin.site.urls),
    # === FIXED AUTH — THIS IS THE ONE THAT WORKS ===
    path("accounts/signup/", include("mysticbox.mysticbox.urls")),  # custom signup form
    path("accounts/", include("allauth.urls")),  # everything else (login, logout, etc)
    path("", include("home.urls")),
    path("boxes/", include("boxes.urls")),
    path("cart/", include("cart.urls")),
    path("services/", include("services.urls")),
    path("market/", include("hecatemarket.urls")),
    path("checkout/", include("checkout.urls")),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
# Stripe webhook
