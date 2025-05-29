from django.db import models


class ServiceBase(models.Model):
    name = models.CharField(max_length=100)
    price = models.DecimalField(max_digits=6, decimal_places=2)

    class Meta:
        abstract = True


# 1. birthchart reading request
class BirthChartRequest(ServiceBase):
    email = models.EmailField()
    birth_date = models.DateField()
    birth_time = models.TimeField()
    birth_place = models.CharField(max_length=100)
    question = models.TextField(blank=True, null=True)
    submitted_on = models.DateTimeField(auto_now_add=True)
    paid = models.BooleanField(default=False)

    def __str__(self):
        return f"Birth chart for {self.name} ({self.email})"


# 2. Ask a witch request
class WitchQuestion(ServiceBase):
    email = models.EmailField()
    question = models.TextField()
    submitted_on = models.DateTimeField(auto_now_add=True)
    paid = models.BooleanField(default=False)

    def __str__(self):
        return f"Question from {self.name}"


# 3. Ritual or spell request
class RitualRequest(ServiceBase):
    email = models.EmailField()
    intention = models.CharField(max_length=200)
    details = models.TextField()
    urgency = models.CharField(max_length=50, choices=[('low', 'Low'), ('medium', 'Medium'), ('high', 'High')])
    submitted_on = models.DateTimeField(auto_now_add=True)
    paid = models.BooleanField(default=False)

    def __str__(self):
        return f"Ritual request from {self.name} - {self.intention}"


# 4. Dream interpretation request
class DreamSubmission(ServiceBase):
    email = models.EmailField()
    dream_description = models.TextField()
    recurring = models.BooleanField(default=False)
    submitted_on = models.DateTimeField(auto_now_add=True)
    paid = models.BooleanField(default=False)

    def __str__(self):
        return f"Dream by {self.name}"


# 5. Medium Contact
class MediumContactRequest(ServiceBase):
    email = models.EmailField()
    message = models.TextField()
    focus_area = models.CharField(max_length=100, blank=True, null=True)
    submitted_on = models.DateTimeField(auto_now_add=True)
    paid = models.BooleanField(default=False)

    def __str__(self):
        return f"Medium contact from {self.name}"
