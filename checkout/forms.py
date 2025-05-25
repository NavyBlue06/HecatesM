from django import forms
from django_countries.widgets import CountrySelectWidget
from .models import Order

class OrderForm(forms.ModelForm):
    promo_code = forms.CharField(
        max_length=20,
        required=False,
        label="Promo Code",
        widget=forms.TextInput(
            attrs={"class": "form-control", "placeholder": "Enter promo code"}
        ),
    )

    class Meta:
        model = Order
        fields = (
            "full_name",
            "email",
            "phone_number",
            "country",
            "postcode",
            "town_or_city",
            "street_address1",
            "street_address2",
            "county",
            "promo_code",  # Include promo code field
        )
        widgets = {
            'country': CountrySelectWidget(attrs={'class': 'form-select'}),
        }
