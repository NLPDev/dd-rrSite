import datetime
from decimal import Decimal
from django.db import models

from community.models import Community
from neighbor.models import Neighbor, Transactions


class Violation(models.Model):
    title = models.CharField(max_length=40)
    fee = models.DecimalField(decimal_places=2, max_digits=9)
    days_to_pay = models.IntegerField(max_length=3, default='30')
    community = models.ForeignKey(Community)

    class Meta:
        verbose_name_plural = 'Violations'
        verbose_name = 'Violation'

    def __unicode__(self):
        return self.title


def get_day_choices():
    days = []
    for i in range(1, 32):
        days.append((i, i))
    return days


class ViolationEvent(models.Model):

    MONTH_CHOICES = [
        (1, 'January'),
        (2, 'February'),
        (3, 'March'),
        (4, 'April'),
        (5, 'May'),
        (6, 'June'),
        (7, 'July'),
        (8, 'August'),
        (9, 'September'),
        (10, 'October'),
        (11, 'November'),
        (12, 'December'),
    ]

    violator = models.ForeignKey(Neighbor, blank=True, null=True)
    violator_address = models.CharField(max_length=100)
    message = models.TextField(blank=True, null=True, verbose_name='Violation Description')
    violation = models.ForeignKey(Violation)
    submitted_on = models.DateTimeField(auto_now_add=True)
    submitted_by = models.ForeignKey(Neighbor, related_name="submitted_by_neighbor")
    due_date = models.DateField(blank=True, null=True)

    event_date_not_relevant = models.BooleanField(default=False)
    event_month = models.IntegerField(blank=True, null=True, max_length=2, choices=MONTH_CHOICES)
    event_day = models.IntegerField(blank=True, null=True, max_length=2, choices=get_day_choices())
    event_start = models.TimeField(blank=True, null=True)
    event_end = models.TimeField(blank=True, null=True)

    # approval and payment information
    is_approved = models.BooleanField(default=False, verbose_name='Approved')
    is_denied = models.BooleanField(default=False, verbose_name='Denied')
    is_paid = models.BooleanField(default=False, verbose_name='Paid')
    transaction = models.ForeignKey(Transactions, blank=True, null=True)

    @property
    def amount(self):
        return Decimal(self.violation.fee)

    @property
    def title(self):
        return self.violation.title

    class Meta:
        verbose_name = 'Violation Event'
        verbose_name_plural = 'Violation Events'

    def save(self, *args, **kwargs):
        if self.violator is None:
            try:
                self.violator = Neighbor.objects.get(address_1=self.violator_address)
            except:
                pass

        if self.is_approved:
            self.due_date = datetime.datetime.today() + datetime.timedelta(days=self.violation.days_to_pay)

        super(ViolationEvent, self).save(*args, **kwargs)

    def __unicode__(self):
        return u'[{}] @ {}'.format(self.violation, self.submitted_on.date())

    def toggle_approved(self):
        if self.is_approved:
            self.is_approved = False
        else:
            self.is_approved = True
            self.due_date = datetime.datetime.today() + datetime.timedelta(days=self.violation.days_to_pay)

        self.save()

    def mark_paid(self, transaction):
        self.transaction = transaction
        self.is_paid = True
        self.save()


class ViolationStep(models.Model):

    sort_order = models.IntegerField(default=100)
    message = models.TextField()
    community = models.ForeignKey(Community)

    class Meta:
        verbose_name_plural = 'Violation Reporting Steps'
        verbose_name = 'Violation Reporting Step'

    def __unicode__(self):
        return self.message[:30] + '...'


class ViolationFaq(models.Model):

    sort_order = models.IntegerField(default=100)
    message = models.TextField()
    community = models.ForeignKey(Community)

    class Meta:
        verbose_name_plural = 'Violation FAQs'
        verbose_name = 'Violation FAQ'

    def __unicode__(self):
        return self.message[:30] + '...'
