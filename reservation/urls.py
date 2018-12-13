from django.conf.urls import patterns, url

urlpatterns = patterns('reservation.views',
                       url(r'^$', 'common_areas', name='common_areas'),
                       url(r'^ajax-related-services/(?P<common_area_id>[0-9]+)/$', 'ajax_related_services'),
                       url(r'^ajax-reservation-form/(?P<common_area_id>[0-9]+)/$', 'ajax_reservation_form'),
					   url(r'^ajax-reservation-payment/$', 'ajax_reservation_payment'),
                       url(r'^ajax-reservation-success/$', 'ajax_reservation_success', name='ajax_reservation_success'),
                       url(r'^ajax-calendar-items/(?P<date>[0-9\-]+)/$', 'ajax_calendar_items', name='ajax_reservation_calendar_items'),
                       url(r'^ajax-calendar-days/$', 'ajax_calendar_days', name='ajax_reservation_calendar_days'),
                       url(r'^ajax-datepicker-times/$', 'ajax_datepicker_times', name='ajax_datepicker_times'),
)