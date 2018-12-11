from django.contrib import admin
from models import *


class ContactAdmin(admin.ModelAdmin):
    search_fields = ('first_name', 'last_name', 'email', 'message')
    list_filter = ('community',)
    list_display = ('date', 'community', 'first_name', 'last_name', 'email')

    class Media:
        js = [
            '/static/admin_js/tinymce/tinymce.min.js',
            '/static/admin_js/tinymce_init.js'
        ]


admin.site.register(ContactLead, ContactAdmin)