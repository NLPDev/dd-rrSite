from django import forms
from django.forms import ModelForm
from datetime import datetime, timedelta
from neighbor.models import CalendarEvent, EventPhoto
from utility import get_time_choices


class CalendarEventForm(ModelForm):

    start_date = forms.ChoiceField(choices=get_time_choices(), label='Start Time')
    end_date = forms.ChoiceField(choices=get_time_choices(), label='End Time')

    def __init__(self, request=None, *args, **kwargs):
        kwargs.setdefault('label_suffix', '')
        super(CalendarEventForm, self).__init__(*args, **kwargs)

    def clean(self):
        cleaned_data = super(CalendarEventForm, self).clean()

        # add the date to the start and end times
        try:
            if datetime.strptime(cleaned_data['end_date'], '%H:%M:%S') <= datetime.strptime(cleaned_data['start_date'], '%H:%M:%S'):
                # handle spans that go past midnight
                date_obj = datetime.strptime(self.data['datepicker_value'], '%Y-%m-%d')
                date_obj = date_obj + timedelta(days=1)
                cleaned_data['end_date'] = date_obj.strftime("%Y-%m-%d") + ' ' + cleaned_data['end_date']
            else:
                cleaned_data['end_date'] = self.data['datepicker_value'] + ' ' + cleaned_data['end_date']
            cleaned_data['start_date'] = self.data['datepicker_value'] + ' ' + cleaned_data['start_date']
        except:
            cleaned_data['start_date'] = None
            cleaned_data['end_date'] = None

        return cleaned_data

    class Meta:
        model = CalendarEvent
        fields = ('title', 'location', 'start_date', 'end_date', 'description', 'first_name', 'last_name', 'phone', 'email',)


class CalendarEventPhotoForm(ModelForm):

    class Meta:
        model = EventPhoto
        fields = ('photo',)