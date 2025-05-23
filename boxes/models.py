from django.db import models


class Product(models.Model):
    name = models.CharField(max_length=254)
    description = models.TextField()
    price = models.DecimalField(max_digits=6, decimal_places=2)
    image = models.ImageField(upload_to="product_images", null=True, blank=True)
    category = models.CharField(max_length=254, default="General")
    is_available = models.BooleanField(default=True)

    def __str__(self):
        return self.name
