__author__ = 'nathanlebert'

from django import forms

from announcement.models import Announcement
from neighbor.models import CalendarEvent, AddressConflict
from service_provider.models import ServiceProvider
from violation.models import ViolationEvent, Violation


class QueueForm(forms.Form):

    def __init__(self, *args, **kwargs):
        super(QueueForm, self).__init__(*args, **kwargs)

        # Dynamically generate our queue fields when our form is instantiated.
        self.fields['violation_events'] = forms.ModelMultipleChoiceField(queryset=ViolationEvent.objects.filter(is_approved=False).order_by('-submitted_on').exclude(is_denied=True), required=False)
        self.fields['service_providers'] = forms.ModelMultipleChoiceField(queryset=ServiceProvider.objects.filter(is_approved=False).exclude(is_denied=True), required=False)
        self.fields['calendar_events'] = forms.ModelMultipleChoiceField(queryset=CalendarEvent.objects.filter(is_approved=False, is_cancelled=False).exclude(is_denied=True), required=False)
        self.fields['announcements'] = forms.ModelMultipleChoiceField(queryset=Announcement.objects.filter(is_approved=False, is_cancelled=False).exclude(is_denied=True), required=False)
        self.fields['address_conflicts'] = forms.ModelMultipleChoiceField(queryset=AddressConflict.objects.filter(is_resolved=False), required=False)

    def save(self, *args, **kwargs):

        to_approve = []

        # Get announcements, find any that need to be approved, append to list.
        announcements = self.cleaned_data['announcements']
        if announcements:
            for announcement in announcements:
                to_approve.append(announcement)

        # Get Violations, find any that need to be approved, append to list.
        violations = self.cleaned_data['violation_events']
        if violations:
            for violation in violations:
                to_approve.append(violation)

        # Get Service Providers, find any that need to be approved, append to list.
        providers = self.cleaned_data['service_providers']
        if providers:
            for provider in providers:
                to_approve.append(provider)

        # Get Calendar Event, find any that need to be approved, append to list.
        c_events = self.cleaned_data['calendar_events']
        if c_events:
            for c_event in c_events:
                to_approve.append(c_event)

        # Get Address Conflicts, find any that need action to be taken, and append to list.
        address_conflicts = self.cleaned_data['address_conflicts']
        if address_conflicts:
            for conflict in address_conflicts:
                to_approve.append(conflict)

        # Approve all in list.
        action = kwargs.get('action')
        for event in to_approve:

            if action == 'deny':
                try:
                    getattr(event, 'is_resolved')
                    event.is_resolved = True
                except Exception:
                    event.is_denied = True
                event.save()

            else:
                try:
                    getattr(event, 'is_resolved')
                    event.is_resolved = True
                except Exception:
                    event.is_approved = True
                event.save()