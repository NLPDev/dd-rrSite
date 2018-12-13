from decimal import Decimal

from django.db import models
from django.conf import settings
from django.utils.dateparse import parse_datetime
import pytz

from community.models import Community
from neighbor.models import Neighbor, Transactions


class ReservableServices(models.Model):
    title = models.CharField(max_length=40)
    description = models.TextField(blank=True, null=True)
    fee = models.DecimalField(default=0.00, decimal_places=2, max_digits=5)

    open = models.TimeField(blank=True, null=True)
    close = models.TimeField(blank=True, null=True)
    turn_around_time = models.IntegerField(blank=True, null=True)

    FIDELITY_CHOICES = (
        ('.25','15 minutes'),
        ('.5','30 minutes'),
        ('1','1 hour'),
        ('2','2 hours'),
        ('4','4 hours'),
    )
    fidelity = models.CharField(max_length=3, choices=FIDELITY_CHOICES, default='1')

    community = models.ForeignKey(Community)
    is_approved = models.BooleanField(default=False, verbose_name='Approved')

    related_service = models.ManyToManyField('self', blank=True, null=True, help_text='Related services that can be booked, like pool and pool house')

    class Meta:
        verbose_name = 'Reservable Service'
        verbose_name_plural = 'Reservable Services'

    def __unicode__(self):
        return self.title

    def toggle_approval(self):
        if self.is_approved:
            self.is_approved = False
        else:
            self.is_approved = True

        self.save()


    def check_if_available(self, hours):

        start_string = hours[0]
        end_string = hours[1]

        start = parse_datetime(start_string)
        end = parse_datetime(end_string)

        response = {'is_available': False, 'message': '', 'error_area': None}

        # check that start and end times are not the same
        if start.time() == end.time():
            response['is_available'] = False
            response['message'] = 'Your start and end times should be different'
            response['error_area'] = 'start_time'
            return response

        # check open/close time
        if self.open:
            if start.time() < self.open:
                response['is_available'] = False
                response['message'] = 'You can\'t book before the {} opens'.format(self.title)
                response['error_area'] = 'start_time'
                return response
        if self.close:
            if end.time() > self.close:
                response['is_available'] = False
                response['message'] = 'You can\'t book after the {} closes'.format(self.title)
                response['error_area'] = 'end_time'
                return response

        # lookup any block overlaps
        try:
            overlapping_block = ReserveBlock.objects.filter(service=self, is_paid=True, is_cancelled=False, end_time__gt=start, start_time__lt=end)
            if overlapping_block:
                response['is_available'] = False
                response['message'] = 'Your booking overlaps another reservation.'
                response['error_area'] = 'start_time'
                return response
        except pytz.NonExistentTimeError:
            # this can occur around the daylight savings clock switch
            response['is_available'] = False
            response['message'] = 'Time does not exist.'
            response['error_area'] = 'start_time'
            return response

        response['is_available'], response['message'] = True, 'This is available!'
        return response


class ReserveBlock(models.Model):
    service = models.ForeignKey(ReservableServices)
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    event_description = models.TextField(blank=True, null=True)

    neighbor = models.ForeignKey(Neighbor)
    is_paid = models.BooleanField(default=False, verbose_name='Paid')
    is_cancelled = models.BooleanField(default=False)

    # Payment association
    transaction = models.ForeignKey(Transactions, blank=True, null=True)

    @property
    def amount(self):
        return Decimal(self.service.fee)

    class Meta:
        verbose_name = 'Reserved Time'
        verbose_name_plural = 'Reserved Times'

    def mark_paid(self, transaction=None):
        self.transaction = transaction
        self.is_paid = True
        self.save()
