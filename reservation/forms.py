from datetime import date, time, datetime, timedelta
from django import forms
from django.forms import ModelForm, ModelMultipleChoiceField
from django.utils.dateparse import parse_date
from django.utils.safestring import mark_safe
from operator import itemgetter
from django.forms.widgets import Select
from django.utils.encoding import force_unicode
from django.utils.html import escape, conditional_escape

from neighbor.helper_classes import ExpiryDateField
from reservation.models import ReserveBlock, ReservableServices

# for a list of given services, return a list of tuples to be used by a choice field
#  of times between the opening of the latest service, and the closing of the earliest service,
#  with the smallest fidelity used for steps.
def get_available_times(services, field, reserve_date=None):

    available_times = []
    reservable_services = []

    if reserve_date is None:
        reserve_date = date.today()

    if type(reserve_date).__name__ != 'datetime.date' and type(reserve_date).__name__ != 'date':
        if type(reserve_date).__name__ == 'unicode':
            import unicodedata
            unicodedata.normalize('NFKD', reserve_date).encode('ascii','ignore')
            reserve_date = parse_date(reserve_date)
        else:
            reserve_date = parse_date(reserve_date)

    min_fidelity = max(ReservableServices.FIDELITY_CHOICES, key=itemgetter(1))[0]
    max_open = time.min
    min_close = time.max

    for service_id in services:
        reservable_service = ReservableServices.objects.get(pk=service_id)
        reservable_services.append(reservable_service) # used later to check availability

        # if this service has the smallest fidelity, use that fidelity
        if reservable_service.fidelity and reservable_service.fidelity < min_fidelity:
            min_fidelity = reservable_service.fidelity
        # if this service has the latest open time, use that open time
        if reservable_service.open and reservable_service.open > max_open:
            max_open = reservable_service.open
        # if this service has the earliest close time, use that close time
        if reservable_service.close and reservable_service.close < min_close:
            min_close = reservable_service.close

    # construct the time list
    time_step = max_open
    do_break = False
    while time_step <= min_close and len(available_times) < 100:

        # calculate our next time step
        dt = datetime.combine(reserve_date, time_step) + timedelta(hours=float(min_fidelity))

        # see if the current time step is available for all services requested
        is_available = True
        for reservable_service in reservable_services:
            if is_available:
                response = reservable_service.check_if_available((str(datetime.combine(reserve_date, time_step)), str(dt)))
                is_available = response['is_available']

        # add time to the list
        if min_close != time.max and time_step == min_close and field == 'start_time':
            # do not allow users to pick a start time equal to the closing time
            pass
        elif max_open != time.min and time_step == max_open and field == 'end_time':
            # do not allow users to pick an end time equal to the opening time
            pass
        elif is_available:
            available_times.append([time_step, {'label': time_step.strftime('%I:%M %p').lstrip('0')}])
        else:
            available_times.append([time_step, {'label': time_step.strftime('%I:%M %p').lstrip('0'), 'disabled': True}])

        # see if we've looped around. if so, add that last time then quit
        if do_break:
            break
        if len(available_times) > 1 and dt.time() < time_step:
            do_break = True
        time_step = dt.time()


    return available_times


# from https://djangosnippets.org/snippets/2453/
class SelectWithDisabled(Select):
    """
    Subclass of Django's select widget that allows disabling options.
    To disable an option, pass a dict instead of a string for its label,
    of the form: {'label': 'option label', 'disabled': True}
    """
    def render_option(self, selected_choices, option_value, option_label):
        option_value = force_unicode(option_value)
        if (option_value in selected_choices):
            selected_html = u' selected="selected"'
        else:
            selected_html = ''
        disabled_html = ''
        if isinstance(option_label, dict):
            if dict.get(option_label, 'disabled'):
                disabled_html = u' disabled="disabled"'
            option_label = option_label['label']
        return u'<option value="%s"%s%s>%s</option>' % (
            escape(option_value), selected_html, disabled_html,
            conditional_escape(force_unicode(option_label)))


class ReservationForm(forms.Form):

    event_description = forms.CharField(max_length=200, required=False)

    def __init__(self, request=None, reservable_service=None, *args, **kwargs):
        kwargs.setdefault('label_suffix', '')
        super(ReservationForm, self).__init__(*args, **kwargs)

        # gather together the list of services to be reserved
        self.services = []
        if reservable_service is not None:
            self.services.append(reservable_service)
        try:
            self.services = self.services + request.session['reservation_related_services']
        except:
            pass

        self.fields['start_time'] = forms.ChoiceField(choices=get_available_times(self.services, 'start_time'), widget=SelectWithDisabled())
        self.fields['end_time'] = forms.ChoiceField(choices=get_available_times(self.services, 'end_time'), widget=SelectWithDisabled())

    def clean(self):
        cleaned_data = super(ReservationForm, self).clean()

        # add the date to the start and end times
        if datetime.strptime(cleaned_data['end_time'], '%H:%M:%S') <= datetime.strptime(cleaned_data['start_time'], '%H:%M:%S'):
            # handle blocks that go past midnight
            date_obj = datetime.strptime(self.data['datepicker_value'], '%Y-%m-%d')
            date_obj = date_obj + timedelta(days=1)
            cleaned_data['end_time'] = date_obj.strftime("%Y-%m-%d") + ' ' + cleaned_data['end_time']
        else:
            cleaned_data['end_time'] = self.data['datepicker_value'] + ' ' + cleaned_data['end_time']
        cleaned_data['start_time'] = self.data['datepicker_value'] + ' ' + cleaned_data['start_time']

        # check if block is available
        hours = (cleaned_data['start_time'], cleaned_data['end_time'])
        for service in self.services:
            available = ReservableServices.objects.get(id=service).check_if_available(hours)

            if not available['is_available']:
                self.add_error(available['error_area'], available['message'])

        return cleaned_data


class RelatedServicesForm(forms.Form):

    def __init__(self, *args, **kwargs):
        base_service = kwargs.pop('base_service')
        super(RelatedServicesForm, self).__init__(*args, **kwargs)
        self.fields['related_service_choices'] = RelatedServicesModelMultipleChoiceField(queryset=ReservableServices.objects.filter(related_service__in=[base_service.id]),
                                                                 widget=forms.CheckboxSelectMultiple(), required=False, label='')

class RelatedServicesModelMultipleChoiceField(ModelMultipleChoiceField):
    def label_from_instance(self, obj):
        if obj.fee <= 0:
            fee_text = 'No reservation fee'
        else:
            fee_text = '$' + str(obj.fee)

        return mark_safe('<span class="checkbox_icon"></span>' + conditional_escape(obj.title) + ' <label class="price">' + conditional_escape(fee_text) + '</label>')


class ReservationPaymentsForm(forms.Form):
    name_on_card = forms.CharField(max_length=200)
    card_number = forms.CharField(max_length=16)
    card_type = forms.ChoiceField(choices=(('V', 'VISA'), ('MC', 'MASTERCARD'), ('AMEX', 'AMERICAN EXPRESS'), ('D', 'DISCOVER')))
    security_code = forms.CharField(max_length=4)
    exp_date = ExpiryDateField(widget=forms.TextInput(attrs={'class': 'form-control'}))