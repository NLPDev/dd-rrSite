from django.db import models

from community.models import Community


class Dues(models.Model):
    PAY_FREQUENCY_CHOICES = (('M', 'Monthly'), ('Y', 'Yearly'))

    community = models.ForeignKey(Community)
    pay_frequency = models.CharField(choices=PAY_FREQUENCY_CHOICES, max_length=2)
    fee = models.DecimalField(max_digits=9, decimal_places=2, default=0.00)
    late_fee = models.DecimalField(max_digits=9, decimal_places=2, blank=True, null=True)
    late_fee_period = models.IntegerField(help_text='Reoccurs after x days (i.e. $10 every month)', blank=True, null=True)
    is_active = models.BooleanField(default=True)
    title = models.CharField(max_length=40)

    class Meta:
        verbose_name = 'Due'
        verbose_name_plural = 'Dues'

    def save(self, *args, **kwargs):
        super(Dues, self).save(*args, **kwargs)

        # Check if the due is still active. If not, make sure neighbors aren't getting notified about 'ghost' fees.
        if not self.is_active:
            for duepayment in self.duepayment_set.all():
                duepayment.is_active = False
                duepayment.save()
        else:
            for duepayment in self.duepayment_set.all():
                duepayment.is_active = True
                duepayment.save()

        super(Dues, self).save(*args, **kwargs)

    def __unicode__(self):
        return self.title