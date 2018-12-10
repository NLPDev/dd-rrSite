from django import forms
from django.forms import ModelForm
from utility import get_time_choices
from violation.models import ViolationEvent

class ViolationForm(ModelForm):

	event_start = forms.ChoiceField(choices=get_time_choices(), required=False)
	event_end = forms.ChoiceField(choices=get_time_choices(), required=False)
	event_date_not_relevant = forms.BooleanField(label='When did this happen', required=False)

	def __init__(self, request=None, *args, **kwargs):
		kwargs.setdefault('label_suffix', '')
		super(ViolationForm, self).__init__(*args, **kwargs)

	class Meta:
		model = ViolationEvent
		fields = ('violator_address', 'violation', 'message', 'event_date_not_relevant', 'event_month', 'event_day', 'event_start', 'event_end')
