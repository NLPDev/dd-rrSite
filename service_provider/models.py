from django.db import models
from easy_thumbnails.fields import ThumbnailerImageField

from neighbor.models import Neighbor
from community.models import Community


def thumbnail_file_name(instance, filename):
    try:
        return '/'.join(['service_provider', str(instance.neighbor.id), filename])
    except Exception:
        return '/'.join(['service_provider', str(instance.community.id), filename])


class ServiceType(models.Model):

    community = models.ForeignKey(Community)
    title = models.CharField(max_length=200)

    class Meta:
        verbose_name_plural = 'Service Types'
        verbose_name = 'Service Type'

    def __unicode__(self):
        return self.title


class ServiceProvider(models.Model):

    community = models.ForeignKey(Community)
    neighbor = models.ForeignKey(Neighbor, blank=True, null=True)
    description = models.TextField(verbose_name='Service Description', blank=True, null=True)
    image = ThumbnailerImageField(upload_to=thumbnail_file_name, blank=True, null=True)
    title = models.CharField(max_length=200, verbose_name='Service Title')
    type = models.ForeignKey(ServiceType)
    phone = models.CharField(max_length=12, verbose_name='Phone Number', blank=True, null=True)
    email = models.EmailField(verbose_name='E-mail Address', blank=True, null=True)
    website = models.CharField(max_length=255, blank=True, null=True)
    facebook = models.CharField(max_length=255, blank=True, null=True)
    twitter = models.CharField(max_length=255, blank=True, null=True)
    linkedin = models.CharField(max_length=255, blank=True, null=True)
    google_plus = models.CharField(max_length=255, blank=True, null=True)

    sort_order = models.IntegerField(default=10)
    created_on = models.DateTimeField(auto_now_add=True)

    is_approved = models.BooleanField(default=False)
    is_denied = models.BooleanField(default=False)

    class Meta:
        verbose_name_plural = 'Service Providers'
        verbose_name = 'Service Provider'

    def __unicode__(self):
        return self.title
