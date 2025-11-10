# mysticbox/mysticbox/urls.py
from django.urls import path
from allauth.account.views import SignupView
from .forms import CustomSignupForm

class FixedSignupView(SignupView):
    form_class = CustomSignupForm

urlpatterns = [
    path("", FixedSignupView.as_view(), name="account_signup"),
]