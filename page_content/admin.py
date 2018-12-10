from django.contrib import admin
from page_content.models import *


class LogoAdmin(admin.ModelAdmin):
    list_display = ('label',)
    save_as = True

    fieldsets = (
        (None, {
            'fields': ('site', 'label', 'image')
        }),
    )


class PageSectionInline(admin.TabularInline):
    model = PageSection
    sortable_field_name = "display_order"
    extra = 1


class WebPageAdmin(admin.ModelAdmin):
    model = WebPage
    list_display = ('label', 'community', 'is_published', 'create_date')
    list_filter = ('modified_date', 'is_published', 'community')
    list_editable = ('is_published',)

    prepopulated_fields = {'slug': ('label',), }
    search_fields = ('label',)
    save_as = True

    inlines = [
        PageSectionInline,
    ]

    fieldsets = (

        (None, {
            'classes': ('suit-tab suit-tab-general full-width',),
            'fields': ('community', 'template_choice', 'template_addon', 'label', 'image_cover', 'is_published')
        }),

        (None, {
            'classes': ('suit-tab suit-tab-seo',),
            'fields': ('meta_title', 'meta_description', 'meta_tags', 'slug')
        }),

    )

    suit_form_includes = (
        ('admin/suit_includes/edit_page_content.html', 'bottom', 'general'),
    )

    suit_form_tabs = (('general', 'General'), ('seo', 'SEO'))


class SocialLinkInline(admin.TabularInline):
    model = FooterSocialLink
    sortable_field_name = 'order'
    extra = 1


class FooterAdmin(admin.ModelAdmin):
    list_display = ('label',)
    save_as = True

    fieldsets = (
        (None, {
            'fields': ('site', 'label')
        }),

    )

    inlines = [
        SocialLinkInline,
    ]

    suit_form_includes = (
        ('admin/suit_includes/edit_footer_content.html', 'bottom', 'general'),
    )


class ModalSuccessAdmin(admin.ModelAdmin):
    list_display = ('modal_name','title',)
    save_as = True


class BillboardAdmin(admin.ModelAdmin):
    model = Billboard
    list_display = ('label', 'community', 'order', 'publish_date', 'is_published')
    list_filter = ('publish_date', 'is_published')
    list_editable = ('order', 'is_published',)
    save_as = True

    fieldsets = (

        (None, {
            'classes': ('full-width',),
            'fields': ('community', 'label', 'order', 'image', 'header', 'sub_header', 'publish_date', 'expire_date', 'is_published')
        }),

    )


class MiniBillboardAdmin(admin.ModelAdmin):
    model = MiniBillboard
    list_display = ('label', 'community', 'order', 'publish_date', 'is_published')
    list_filter = ('publish_date', 'is_published')
    list_editable = ('order', 'is_published',)
    ordering = ('community', 'order', 'publish_date')
    save_as = True

    fieldsets = (

        (None, {
            'classes': ('full-width',),
            'fields': ('community', 'label', 'order', 'image', 'link', 'publish_date', 'expire_date', 'is_published')
        }),

    )


admin.site.register(Logo, LogoAdmin)
admin.site.register(WebPage, WebPageAdmin)
admin.site.register(Footer, FooterAdmin)
admin.site.register(ModalSuccess, ModalSuccessAdmin)
admin.site.register(Billboard, BillboardAdmin)
admin.site.register(MiniBillboard, MiniBillboardAdmin)