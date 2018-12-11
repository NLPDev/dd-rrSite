from django.contrib.sites.models import Site
from django.db import models

from neighbor.models import Neighbor
from community.models import Community


class ContactLead(models.Model):
    first_name = models.CharField(max_length=100, blank=True, null=True)
    last_name = models.CharField(max_length=100, blank=True, null=True)
    phone = models.CharField(max_length=20, blank=True, null=True)
    email = models.CharField(max_length=100, blank=True, null=True)
    message = models.TextField(max_length=1000)
    preferred_method = models.CharField(max_length=10, choices=(('email','Email'),('phone','Phone'),), blank=False, null=False, default='email', verbose_name='Preferred Contact Method')

    neighbor = models.ForeignKey(Neighbor)
    community = models.ForeignKey(Community)

    date = models.DateTimeField()

    def __unicode__(self):
        return self.first_name

    class Meta:
        verbose_name_plural = 'Contact Leads'
        verbose_name = 'Contact Lead'
        ordering = ('-date', 'first_name', 'last_name')
