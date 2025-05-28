from django.db import models
from cloudinary.models import CloudinaryField  #  import CloudinaryField


class Product(models.Model):
    name = models.CharField(max_length=254)
    description = models.TextField()
    price = models.DecimalField(max_digits=6, decimal_places=2)
    image = CloudinaryField("image", null=True, blank=True)  #  switched from ImageField
    category = models.CharField(max_length=254, default="General")
    is_available = models.BooleanField(default=True)
    sku = models.CharField(max_length=32, null=True, blank=True)  # Stock Keeping Unit

    def __str__(self):
        return self.name
