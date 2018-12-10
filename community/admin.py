from django.contrib import admin
from django.core.urlresolvers import reverse
from django.utils.html import format_html

from violation.models import Violation
from dues.models import Dues
from community.models import Community, Document


class DuesInline(admin.TabularInline):
    model = Dues
    extra = 0


class ViolationInline(admin.TabularInline):
    model = Violation
    extra = 0


class CommunityAdmin(admin.ModelAdmin):
    model = Community
    list_display = ('name', 'city', 'state', 'created_on', 'community_edit')
    readonly_fields = ('slug', 'created_on', )
    inlines = [ViolationInline, DuesInline, ]

    # search/filtering
    list_filter = ('state', 'city', )
    search_fields = ['name', 'slug', ]
    save_as = True

    fieldsets = (
        (None, {
            'classes': ('suit-tab suit-tab-general full-width',),
            'fields': ('name', 'city', 'state', 'zip_code', 'slug', 'created_on')
        }),
        ('Stripe Information', {
            'classes': ('suit-tab suit-tab-stripe',),
            'fields': ('debug_mode', 'production_public', 'production_secret', 'testing_public', 'testing_secret')
        }),
    )

    suit_form_tabs = (('general', 'General'), ('stripe', 'Stripe Information'))

    def community_edit(self, instance):
        return format_html('<a href="' + reverse('community:admin_edit', kwargs={'community_id': instance.id}) + '">Edit Site</a>')
    community_edit.allow_tags = True


class DocumentAdmin(admin.ModelAdmin):
    model = Document
    list_display = ('title', 'document', 'community')

    # search/filtering
    list_filter = ('community', )
    search_fields = ['title', 'document', 'description']
    save_as = True

admin.site.register(Community, CommunityAdmin)
admin.site.register(Document, DocumentAdmin)
