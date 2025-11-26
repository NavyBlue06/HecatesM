from uuid import uuid4
from django.db import models
from django.db.models import Sum
from django.conf import settings
from boxes.models import Product
from django_countries.fields import CountryField
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType


class Order(models.Model):
    order_number = models.CharField(max_length=32, null=False, editable=False)

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="orders",
    )

    full_name = models.CharField(max_length=50, null=False, blank=False)
    email = models.EmailField(max_length=254, null=False, blank=False)
    phone_number = models.CharField(max_length=20, null=False, blank=False)

    promo_code = models.CharField(max_length=20, blank=True, null=True)
    discount_amount = models.DecimalField(
        max_digits=6,
        decimal_places=2,
        default=0.00,
    )

    country = CountryField(blank_label="(Select country)", null=False, blank=False)
    postcode = models.CharField(max_length=20, null=True, blank=True)
    town_or_city = models.CharField(max_length=40, null=False, blank=False)
    street_address1 = models.CharField(max_length=80, null=False, blank=False)
    street_address2 = models.CharField(max_length=80, null=True, blank=True)
    county = models.CharField(max_length=80, null=True, blank=True)

    stripe_pid = models.CharField(
        max_length=254,
        null=False,
        blank=False,
        default="",
    )

    date = models.DateTimeField(auto_now_add=True)

    delivery_cost = models.DecimalField(
        max_digits=6,
        decimal_places=2,
        null=False,
        default=0,
    )

    order_total = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=False,
        default=0,
    )

    grand_total = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=False,
        default=0,
    )

    def _generate_order_number(self):
        return uuid4().hex.upper()

    def update_total(self):
        self.order_total = (
            self.lineitems.aggregate(Sum("lineitem_total"))["lineitem_total__sum"] or 0
        )

        if self.order_total < settings.FREE_DELIVERY_THRESHOLD:
            self.delivery_cost = (
                self.order_total * settings.STANDARD_DELIVERY_PERCENTAGE / 100
            )
        else:
            self.delivery_cost = 0

        self.grand_total = self.order_total + self.delivery_cost - self.discount_amount
        self.save()

    def save(self, *args, **kwargs):
        if not self.order_number:
            self.order_number = self._generate_order_number()
        super().save(*args, **kwargs)

    def __str__(self):
        return self.order_number


class OrderLineItem(models.Model):
    order = models.ForeignKey(
        Order,
        null=False,
        blank=False,
        on_delete=models.CASCADE,
        related_name="lineitems",
    )

    content_type = models.ForeignKey(
        ContentType,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
    )

    object_id = models.PositiveIntegerField(null=True, blank=True)
    product = GenericForeignKey("content_type", "object_id")

    quantity = models.IntegerField(
        null=False,
        blank=False,
        default=1,
    )

    lineitem_total = models.DecimalField(
        max_digits=6,
        decimal_places=2,
        null=False,
        blank=False,
        editable=False,
    )

    def save(self, *args, **kwargs):
        if self.product:
            self.lineitem_total = self.product.price * self.quantity
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.product} on order {self.order.order_number}"
