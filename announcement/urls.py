__author__ = 'nathanlebert'
from django.conf.urls import patterns, include, url

urlpatterns = patterns('announcement.views',
                        url(r'^$', 'announcements', name='announcements'),
                        url(r'^ajax-add-announcement/$', 'ajax_add_announcement', name='ajax_add_announcement'),
                        url(r'^ajax-announcement-success/$', 'ajax_announcement_success', name='ajax_announcement_success'),
                        url(r'^(?P<announcement_id>[0-9]+)/$', 'announcement_details', name='announcement_details'),
)