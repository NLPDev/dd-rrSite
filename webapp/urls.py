from django.conf.urls import patterns, include, url
from django.conf import settings
from django.contrib import admin

# from neighbor import views as neighbor_views

admin.autodiscover()

urlpatterns = patterns(
    'webapp.views',
    url(r'^$', 'view_home', name='home'),
)

urlpatterns += patterns(
    '',
    url(r'^front-edit/', include('front.urls')),
)

urlpatterns += patterns(
    '',
    url(r'^admin/$', 'dashboard.views.dashboard', name='dashboard'),
    url(r'^admin/filebrowser/', include('filebrowser.urls')),
    url(r'^admin/', include(admin.site.urls)),
    url(r'^super-su/$', 'dashboard.views.superuser_su', name='super_su'),

    url(r'^', include('neighbor.urls')),
    url(r'^community/', include('community.urls', namespace='community', app_name='community')),
    url(r'^violations/', include('violation.urls', namespace='violation', app_name='violation')),
    url(r'^service-providers/', include('service_provider.urls', namespace='service_provider', app_name='service_provider')),
    url(r'^common-areas/', include('reservation.urls', namespace='reservation', app_name='reservation')),
    url(r'^announcements/', include('announcement.urls', namespace='announcement', app_name='announcement')),
)

if settings.DEVELOPMENT:
    urlpatterns += patterns(
        '',
        url(r'^media/(?P<path>.*)$', 'django.views.static.serve', {'document_root': settings.MEDIA_ROOT}),
    )

# should always be last. check for community url
urlpatterns += patterns(
    '',
    url(r'^(?P<path>[-\w\d]+)/', include('community.urls', namespace='community', app_name='community')),
)
