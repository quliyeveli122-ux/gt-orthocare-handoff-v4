from django import forms
from django.core.validators import RegexValidator

phone_validator = RegexValidator(
    r"^\+?[0-9 \-()]{9,20}$",
    "Enter a valid phone number, e.g. +995 5XX XX XX XX",
)


class CheckoutForm(forms.Form):
    customer_name = forms.CharField(max_length=120)
    phone = forms.CharField(max_length=30, validators=[phone_validator])
    city = forms.CharField(max_length=80)
    address = forms.CharField(max_length=250)
    comment = forms.CharField(widget=forms.Textarea(attrs={"rows": 3}), required=False)
