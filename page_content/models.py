from django.contrib.sites.models import Site
from django.db import models
import datetime
from django.db.models import Q
from community.models import Community

try:
    from third_party.filebrowser.fields import FileBrowseField
except ImportError:
    from filebrowser.fields import FileBrowseField


class Logo(models.Model):
    site = models.OneToOneField(Site)
    label = models.CharField(max_length=100, help_text='This is only used in the admin.')
    image = FileBrowseField(max_length=400, blank=True, null=True, help_text='Transparent .png')

    def __unicode__(self):
        return self.label

    class Meta:
        verbose_name = 'Logo'
        verbose_name_plural = 'Logo'


TEMPLATE_CHOICES = (
    ('landing', 'Landing Page'),
    ('1_col', '1 Column'),
    ('1_col_contact', '1 Column w/ Contact Form'),
    ('2_col', '2 Column'),
)

TEMPLATE_ADD_ONS = (
    ('none', 'None'),
    ('staff', 'Staff'),
    ('faq', 'FAQs'),
)


class WebPage(models.Model):

    community = models.ForeignKey(Community)

    template_choice = models.CharField(max_length=50, blank=True, null=True, choices=TEMPLATE_CHOICES, default='1_col')
    template_addon = models.CharField(max_length=50, blank=True, null=True, choices=TEMPLATE_ADD_ONS, default='none')

    label = models.CharField(max_length=100)
    slug = models.SlugField()

    meta_title = models.CharField(max_length=100, blank=True, null=True, help_text='This shows at the top of the browser, usually in the tab.')
    meta_description = models.CharField(max_length=500, blank=True, null=True)
    meta_tags = models.CharField(max_length=500, blank=True, null=True)

    image_cover = FileBrowseField(max_length=400, blank=True, null=True, help_text='Roughly 1400px by 400px', verbose_name='Cover image')

    is_published = models.BooleanField(default=True)
    create_date = models.DateTimeField(auto_now_add=True)
    modified_date = models.DateTimeField(auto_now=True)

    def __unicode__(self):
        return self.label

    def url(self):
        return '/%s/%s' % (self.community.slug, self.slug)

    def get_absolute_url(self):
        return self.url()

    class Meta:
        verbose_name = 'Page'
        verbose_name_plural = 'Pages'
        ordering = ('label',)

    def sections(self):
        return self.pagesection_set.filter(is_published=True)

    @staticmethod
    def get_published_objects():
        return WebPage.objects.filter(is_published=True)


class PageSection(models.Model):
    page = models.ForeignKey(WebPage)
    label = models.CharField(max_length=400)

    image = FileBrowseField(max_length=400, blank=True, null=True, verbose_name='Section image', help_text='At least 1140px wide')

    display_order = models.IntegerField(default=1, verbose_name='Order')
    is_published = models.BooleanField(default=True)

    def __unicode__(self):
        return self.label

    class Meta:
        verbose_name = 'Section'
        verbose_name_plural = 'Sections'
        ordering = ('display_order', 'label')

    @staticmethod
    def get_published_objects():
        objects = PageSection.objects.filter(is_published=True).order_by('display_order', 'label')

        return objects

class Footer(models.Model):
    site = models.OneToOneField(Site)
    label = models.CharField(max_length=100, help_text='This is only used in the admin.')

    def __unicode__(self):
        return self.label

    class Meta:
        verbose_name = 'Footer'
        verbose_name_plural = 'Footer'

    def social_links(self):
        return self.footersociallink_set.order_by('order')


class FooterSocialLink(models.Model):
    parent = models.ForeignKey(Footer)
    label = models.CharField(max_length=200)

    image = FileBrowseField(max_length=400)
    link = models.URLField()

    order = models.IntegerField(default=1)

    def __unicode__(self):
        return self.label

    class Meta:
        verbose_name = 'Social Link'
        verbose_name_plural = 'Social Links'
        ordering = ('order', 'label')


class ModalSuccess(models.Model):
    modal_name = models.CharField(max_length=100, unique=True)
    title = models.CharField(max_length=200, blank=True, null=True)
    message = models.TextField(blank=True, null=True)

    def __unicode__(self):
        return self.modal_name

    class Meta:
        verbose_name = 'Pop-Up Success Message'
        verbose_name_plural = 'Pop-Up Success Messages'
        ordering = ('modal_name',)

    @staticmethod
    def get_content(modal_name, default_title, default_message):
        try:
            content = ModalSuccess.objects.get(modal_name=modal_name)
        except ModalSuccess.DoesNotExist:
            content = ModalSuccess(modal_name=modal_name, title=default_title, message=default_message)
            content.save()

        return content


TEMPLATES = (
    ('billboard', 'Billboards'),
    ('mini_billboard', 'Mini Billboards'),
    ('slide', 'Slide Show'),
    ('2_col', '2 Column Free Form'),
    ('benefit_group', 'Benefit Groups')
)


SLIDE_SHOW_POSITION = (
    ('l', 'Left'),
    ('r', 'Right')
)


BACKGROUND_SIZE = (
    ('n', 'Natural'),
    ('c', 'Cover')
)


class Billboard(models.Model):
    community = models.ForeignKey(Community)
    label = models.CharField(max_length=200)

    image = FileBrowseField(max_length=200, help_text='Approximately 1000 px wide by 650 px tall. (Keep subject towards the middle of image for best viewing on mobile.)')
    header = models.CharField(max_length=35, blank=True, null=True)
    sub_header = models.CharField(max_length=100, blank=True, null=True)
    link = models.CharField(max_length=200, blank=True, null=True)

    is_published = models.BooleanField(default=True)
    publish_date = models.DateField(db_index=True)
    expire_date = models.DateField(null=True, blank=True)

    order = models.IntegerField(default=1)

    def __unicode__(self):
        return self.label

    class Meta:
        verbose_name = 'Billboard'
        verbose_name_plural = 'Billboards'
        ordering = ('order', '-publish_date')

    @staticmethod
    def get_published_objects(community):
        billboards = Billboard.objects.filter(Q(publish_date__lte=datetime.datetime.now) & Q(is_published=True) & Q(community=community) &
                                              (Q(expire_date=None) | Q(expire_date__gte=datetime.datetime.now))).order_by('order', '-publish_date')
        return billboards


class MiniBillboard(models.Model):
    community = models.ForeignKey(Community)
    label = models.CharField(max_length=200)

    image = FileBrowseField(max_length=200, blank=True, null=True)
    link = models.CharField(max_length=200, blank=True, null=True)

    is_published = models.BooleanField(default=True)
    publish_date = models.DateField(db_index=True)
    expire_date = models.DateField(null=True, blank=True)

    order = models.IntegerField(default=1)

    def __unicode__(self):
        return self.label

    class Meta:
        verbose_name = 'Mini Billboard'
        verbose_name_plural = 'Mini Billboards'
        ordering = ('order', '-publish_date')

    @staticmethod
    def get_published_objects(community):
        mini_billboards = MiniBillboard.objects.filter(Q(publish_date__lte=datetime.datetime.now) & Q(is_published=True) & Q(community=community) &
                                                       (Q(expire_date=None) | Q(expire_date__gte=datetime.datetime.now))).order_by('order', '-publish_date')
        return mini_billboards
