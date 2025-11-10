# mysticbox/forms.py
from allauth.account.forms import SignupForm
from django import forms
from django.contrib.auth import get_user_model

User = get_user_model()

class CustomSignupForm(SignupForm):
    def clean(self):
        cleaned_data = super().clean()
        username = cleaned_data.get("username")
        email = cleaned_data.get("email")

        if not username and not email:
            raise forms.ValidationError(
                "You must provide either a username or an email address."
            )

        # Auto-create username from email if missing
        if email and not username:
            base = email.split("@")[0].lower()
            username = "".join(c for c in base if c.isalnum())[:25]
            if not username:
                username = "witch"
            final = username
            i = 1
            while User.objects.filter(username=final).exists():
                final = f"{username}{i}"
                i += 1
            cleaned_data["username"] = final

        return cleaned_data