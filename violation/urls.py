from django.conf.urls import patterns, url

urlpatterns = patterns('violation.views',
                       url(r'^$', 'index', name='violation_index'),
                       url(r'^ajax-report/$', 'ajax_report'),
                       url(r'^ajax-report-success/$', 'ajax_report_success'),
)