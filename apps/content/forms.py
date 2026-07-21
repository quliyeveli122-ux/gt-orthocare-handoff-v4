from django import forms

from apps.orders.forms import phone_validator

from .models import ContactMessage


class ContactForm(forms.ModelForm):
    phone = forms.CharField(max_length=30, validators=[phone_validator])

    class Meta:
        model = ContactMessage
        fields = ["name", "phone", "message"]
        widgets = {"message": forms.Textarea(attrs={"rows": 4})}
