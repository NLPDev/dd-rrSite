from django.contrib import admin

from announcement.models import Announcement, Tag


class TagAdmin(admin.ModelAdmin):
    model = Tag
    list_display = ('title', 'display_order', 'community')

    list_filter = ('community',)
    save_as = True


class AnnouncementAdmin(admin.ModelAdmin):
    model = Announcement
    list_display = ('title', 'event_date', 'approved_date', 'is_approved', 'neighbor', 'community')
    fields = ('community', 'neighbor', 'title', 'content', 'event_date', 'is_approved', 'tags', 'photo')

    list_filter = ('community', 'event_date', 'is_approved')
    search_fields = ['community__name', 'title', 'neighbor__user__email', 'neighbor__user__first_name', 'neighbor__user__last_name']
    save_as = True

admin.site.register(Tag, TagAdmin)
admin.site.register(Announcement, AnnouncementAdmin)