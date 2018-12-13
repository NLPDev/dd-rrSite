from django.contrib import admin

from reservation.models import ReservableServices, ReserveBlock


class ReservableServicesAdmin(admin.ModelAdmin):
    model = ReservableServices
    list_display = ('title', 'fee', 'description', 'open', 'close', 'turn_around_time', 'is_approved', 'community')

    list_filter = ('community', 'is_approved')
    search_fields = ['title', 'fee', 'community__name']
    save_as = True


class ReserveBlockAdmin(admin.ModelAdmin):
    model = ReserveBlock
    list_display = ('neighbor', 'service', 'start_time', 'end_time')

    list_filter = ('neighbor__community', 'service', 'is_paid')
    search_fields = ['service__title', 'service__description', 'event_description', 'neighbor__user__email', 'neighbor__user__first_name', 'neighbor__user__last_name',]
    save_as = True


admin.site.register(ReserveBlock, ReserveBlockAdmin)
admin.site.register(ReservableServices, ReservableServicesAdmin)