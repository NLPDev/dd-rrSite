from django.conf.urls import patterns, url

urlpatterns = patterns('service_provider.views',
                        url(r'^$', 'service_providers', name='service_provider_index'),
						url(r'^ajax-add-provider/$', 'ajax_add_provider', name='ajax_add_service_provider'),
						url(r'^ajax-add-provider-success/$', 'ajax_add_provider_success', name='ajax_add_provider_success'),
)