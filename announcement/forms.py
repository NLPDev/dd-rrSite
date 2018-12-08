from django import forms
from django.forms import ModelForm
from datetime import datetime, timedelta
from announcement.models import Announcement


class AnnouncementForm(ModelForm):

	def __init__(self, request=None, *args, **kwargs):
		kwargs.setdefault('label_suffix', '')
		super(AnnouncementForm, self).__init__(*args, **kwargs)

	def clean(self):
		cleaned_data = super(AnnouncementForm, self).clean()

		try:
			cleaned_data['event_date'] = datetime.strptime(self.data['datepicker_value'], '%Y-%m-%d')
		except:
			raise forms.ValidationError("Event date is invalid.")

		return cleaned_data

	class Meta:
		model = Announcement
		fields = ('title', 'content', 'photo',)