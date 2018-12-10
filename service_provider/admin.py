from django.contrib import admin
from service_provider.models import ServiceProvider, ServiceType


class ServiceProviderAdmin(admin.ModelAdmin):
    model = ServiceProvider
    list_display = ('title', 'type', 'is_approved', 'community')

    list_filter = ('community', 'type', 'is_approved', 'is_denied')
    search_fields = ['description', 'title', 'phone', 'email', 'website', 'neighbor__user__email', 'neighbor__user__first_name', 'neighbor__user__last_name']
    save_as = True


class ServiceTypeAdmin(admin.ModelAdmin):
    model = ServiceType
    list_display = ('title', 'community')
    list_filter = ('community',)
    save_as = True

admin.site.register(ServiceProvider, ServiceProviderAdmin)
admin.site.register(ServiceType, ServiceTypeAdmin)
