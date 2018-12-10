from django.conf.urls import patterns, url
from page_content.views import view_web_page

urlpatterns = patterns('community.views',
                        url(r'^$', 'index', name='community_index'),
                        url(r'^edit/(?P<community_id>[0-9]+)/$', 'admin_edit', name='admin_edit'),
                        url(r'^calendar/$', 'calendar', name='calendar'),
                        url(r'^resources/$', 'resources', name='resources'),
                        url(r'^documents/$', 'documents', name='documents'),
                        url(r'^event/(?P<event_id>[0-9]+)/$', 'event_details', name='event_details'),
                        url(r'^ajax-add-calendar-event/$', 'ajax_add_calendar_event', name='ajax_community_add_calendar_event'),
                        url(r'^ajax-calendar-event-success/$', 'ajax_calendar_event_success', name='ajax_community_calendar_event_success'),
                        url(r'^ajax-calendar-days/$', 'ajax_calendar_days', name='ajax_community_calendar_days'),
                        url(r'^ajax-calendar-items/(?P<date>[0-9\-]+)/$', 'ajax_calendar_items', name='ajax_community_calendar_items'),
                        url(r'^(?P<a_slug>.*)/$', view_web_page),
)