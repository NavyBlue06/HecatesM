from django.db import models
from cloudinary.models import CloudinaryField  # import CloudinaryField

class MagicalItem(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()
    price = models.DecimalField(max_digits=6, decimal_places=2)
    image = CloudinaryField("image", blank=True, null=True)  # switched from ImageField
    is_available = models.BooleanField(default=True)
    sku = models.CharField(max_length=32, null=True, blank=True)  # Stock Keeping Unit

    def __str__(self):
        return self.name
