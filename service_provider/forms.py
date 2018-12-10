from django import forms
from django.forms import ModelForm
from datetime import datetime, timedelta
from service_provider.models import ServiceProvider


class ServiceProviderForm(ModelForm):

	def __init__(self, request=None, *args, **kwargs):
		kwargs.setdefault('label_suffix', '')
		super(ServiceProviderForm, self).__init__(*args, **kwargs)

	class Meta:
		model = ServiceProvider
		fields = ('title', 'type', 'phone', 'email', 'website', 'facebook', 'twitter', 'linkedin', 'google_plus', 'description')