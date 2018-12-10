from django.contrib import admin
from violation.models import *


class ViolationAdmin(admin.ModelAdmin):
    model = Violation
    list_display = ('title', 'fee', 'community')

    list_filter = ('community', )
    search_fields = ['title', 'fee']
    save_as = True


class ViolationEventAdmin(admin.ModelAdmin):
    model = ViolationEvent
    list_display = ('violation', 'submitted_by', 'violator', 'violator_address', 'submitted_on', 'due_date', 'is_approved', 'is_paid', 'community')
    fields = ('submitted_by', 'violator_address', 'message', 'violation', 'event_date_not_relevant', 'event_month', 'event_day', 'event_start', 'event_end', 'is_approved', 'is_paid')

    list_filter = ('violation__community', 'violation', 'is_approved', 'is_paid')
    search_fields = ['violator_address', 'violator__email', 'violator__phone', 'violator__first_name', 'violator__last_name', 'submitted_by__email', 'submitted_by__phone', 'submitted_by__first_name', 'submitted_by__last_name' ]
    save_as = True

    def community(self, instance):
        return instance.submitted_by.community

    def queryset(self, request):
        qs = super(ViolationEventAdmin, self).queryset(request)

        return qs.exclude(is_denied=True)


class ViolationStepAdmin(admin.ModelAdmin):
    model = ViolationStep
    list_display = ('__unicode__', 'sort_order', 'community')

    list_filter = ('community', )
    search_fields = ['message', 'community__name']
    save_as = True


class ViolationFaqAdmin(admin.ModelAdmin):
    model = ViolationFaq
    list_display = ('__unicode__', 'sort_order', 'community')

    list_filter = ('community', )
    search_fields = ['message', 'community__name']
    save_as = True


admin.site.register(Violation, ViolationAdmin)
admin.site.register(ViolationEvent, ViolationEventAdmin)
admin.site.register(ViolationStep, ViolationStepAdmin)
admin.site.register(ViolationFaq, ViolationFaqAdmin)