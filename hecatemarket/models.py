from django.db import models
from cloudinary.models import CloudinaryField  #  cloudinary

class MagicalItem(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()
    price = models.DecimalField(max_digits=6, decimal_places=2)
    image = CloudinaryField("image", blank=True, null=True)  #  cloudinary
    is_available = models.BooleanField(default=True)

    def __str__(self):
        return self.name
