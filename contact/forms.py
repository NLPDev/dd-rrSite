from django import forms
from contact.models import ContactLead


class ContactForm(forms.ModelForm):
    class Meta:
        model = ContactLead
        fields = ('email', 'phone', 'preferred_method', 'message')
        widgets = {
            'preferred_method': forms.RadioSelect,
        }