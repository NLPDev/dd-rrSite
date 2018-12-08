import datetime
from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models
from easy_thumbnails.fields import ThumbnailerImageField
from neighbor.models import Neighbor
from community.models import Community


class Tag(models.Model):
    title = models.CharField(max_length=40)
    display_order = models.IntegerField(default=1)
    is_public = models.BooleanField(default=False)
    community = models.ForeignKey(Community)

    def __unicode__(self):
        return self.title


def validate_photo(fieldfile_obj):
    filesize = fieldfile_obj.file.size
    if filesize > settings.MAX_FILESIZE*1024*1024:
        raise ValidationError("Image exceeds max filesize of %s MB" % str(settings.MAX_FILESIZE))


class Announcement(models.Model):

    title = models.CharField(max_length=40)
    event_date = models.DateField()
    approved_date = models.DateField(blank=True, null=True)
    content = models.TextField(verbose_name='Description')
    photo = ThumbnailerImageField(upload_to='announcements/%Y/%m/%d', blank=True, null=True, validators=[validate_photo])
    tags = models.ManyToManyField(Tag, blank=True, null=True)

    neighbor = models.ForeignKey(Neighbor)
    community = models.ForeignKey(Community)

    is_approved = models.BooleanField(default=False)
    is_denied = models.BooleanField(default=False)
    is_cancelled = models.BooleanField(default=False)

    def save(self, *args, **kwargs):
        if self.is_approved:
            self.approved_date = datetime.datetime.now()

        else:
            self.approved_date = None

        super(Announcement, self).save(*args, **kwargs)

    def __unicode__(self):
        return self.title

    def toggle_approval(self):
        if self.is_approved:
            self.is_approved = False
        else:
            self.is_approved = True

        self.save()

    @staticmethod
    def get_published_objects(community):
        announcements = Announcement.objects.filter(community=community, event_date__gte=datetime.datetime.now, is_approved=True, is_cancelled=False).order_by('event_date', '-approved_date')
        return announcements

