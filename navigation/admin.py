from django.contrib import admin
from models import *


class InlineSubNav(admin.TabularInline):
    model = SubPrimaryNavigation
    sortable_field_name = "order"
    exclude = ('link_type',)


class PrimaryNavigationAdmin(admin.ModelAdmin):
    list_display = ('title', 'is_published', 'order')
    list_editable = ('is_published', 'order')

    search_fields = ('title',)
    save_as = True

    inlines = [
        InlineSubNav,
    ]

    fieldsets = (

        (None, {
            'classes': ('full-width',),
            'fields': ('title', 'order', 'link_type', 'page', 'link', 'is_published')
        }),

    )

    class Media:
        js = [
            '/static/admin_js/custom/navigation.js',
        ]


class SubPrimaryNavigationAdmin(admin.ModelAdmin):
    list_display = ('title', 'parent', 'is_published', 'order')
    list_editable = ('is_published', 'order')

    search_fields = ('title',)
    save_as = True

    fieldsets = (

        (None, {
            'classes': ('full-width',),
            'fields': (
                'parent', 'title', 'page', 'link', 'is_published', 'order'
            )
        }),

    )

    class Media:
        js = [
            '/static/admin_js/custom/navigation.js',
        ]


class TopperNavigationAdmin(admin.ModelAdmin):
    list_display = ('title', 'is_published', 'order')
    list_editable = ('is_published', 'order')

    search_fields = ('title',)
    save_as = True

    fieldsets = (

        (None, {
            'classes': ('full-width',),
            'fields': ('title', 'order', 'link_type', 'page', 'link', 'is_published')
        }),

    )

    class Media:
        js = [
            '/static/admin_js/custom/navigation.js',
        ]


admin.site.register(PrimaryNavigation, PrimaryNavigationAdmin)
admin.site.register(SubPrimaryNavigation, SubPrimaryNavigationAdmin)
admin.site.register(TopperNavigation, TopperNavigationAdmin)