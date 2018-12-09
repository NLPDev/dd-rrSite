from django.contrib import admin
from django.contrib.admin import SimpleListFilter
from django.utils.translation import ugettext_lazy as _
from neighbor.helper_classes import export_xlsx, export_csv
from neighbor.models import Neighbor, CalendarEvent, Wallet, Transactions


class WalletInline(admin.StackedInline):
    model = Wallet
    readonly_fields = ('transactions', )
    extra = 0

    def transactions(self, instance):
        transactions = []

        # Need to look into nested inlines or custom html for this, otherwise it's going to get messy.
        for transaction in instance.transactions_set.all():
            transactions.append('{title} - {date} - {paid} - {amount} - {stripe_id}'.format(title=transaction.title,
                                                                              date=transaction.date,
                                                                              paid=transaction.stripe_paid,
                                                                              amount=transaction.amount,
                                                                              stripe_id=transaction.stripe_id))

        return transactions


class EventInline(admin.StackedInline):
    model = CalendarEvent
    extra = 0


class NeighborAdmin(admin.ModelAdmin):
    model = Neighbor
    list_display = ('first_name', 'last_name', 'phone', 'email', 'preferred_contact_method', 'community')
    inlines = [EventInline]

    list_filter = ('city', 'state', 'zip_code', 'community', 'position', 'preferred_contact_method')
    search_fields = ['user__first_name', 'user__last_name', 'user__email', 'phone', 'address_1', 'user__username']
    save_as = True


class CalendarEventAdmin(admin.ModelAdmin):
    model = CalendarEvent
    list_display = ('title', 'calendar', 'start_date', 'is_approved')

    search_fields = ['title', 'location', 'description', 'first_name', 'last_name', 'phone', 'email']
    save_as = True


class AmountListFilter(SimpleListFilter):
    title = _('Amount')
    parameter_name = 'amount'

    def lookups(self, request, model_admin):
        """
        Returns a list of tuples. The first element in each
        tuple is the coded value for the option that will
        appear in the URL query. The second element is the
        human-readable name for the option that will appear
        in the right sidebar.
        """
        return (
            ('0', _('0')),
            ('10', _('0 - 10')),
            ('50', _('10 - 50')),
            ('100', _('50 - 100')),
            ('300', _('100 - 300')),
            ('300_plus', _('> 300')),
        )

    def queryset(self, request, queryset):
        """
        Returns the filtered queryset based on the value
        provided in the query string and retrievable via
        `self.value()`.
        """
        if self.value() == '0':
            return queryset.filter(amount__lte=0)
        if self.value() == '10':
            return queryset.filter(amount__gt=0, amount__lte=10)
        if self.value() == '50':
            return queryset.filter(amount__gt=10, amount__lte=50)
        if self.value() == '100':
            return queryset.filter(amount__gt=50, amount__lte=100)
        if self.value() == '300':
            return queryset.filter(amount__gt=100, amount__lte=300)
        if self.value() == '300_plus':
            return queryset.filter(amount__gt=300)


class TransactionsAdmin(admin.ModelAdmin):
    model = Transactions
    list_display = ('title', 'date', 'amount', 'stripe_paid', 'transaction_type')
    fields = ('transaction_neighbor', 'title', 'stripe_paid', 'transaction_type', 'amount', 'stripe_id', 'failure_code', 'failure_message',)
    readonly_fields = ('transaction_neighbor',)

    list_filter = ('stripe_paid', 'transaction_type', AmountListFilter,)
    search_fields = ['wallet__neighbor__user__first_name', 'wallet__neighbor__user__last_name', 'wallet__neighbor__user__email',]
    save_as = True

    def transaction_neighbor(self, obj):
        return u'<a href="/admin/neighbor/neighbor/%d/">%s</a>' % (obj.wallet.neighbor.id, obj.wallet.neighbor)
    transaction_neighbor.short_description = 'Neighbor'
    transaction_neighbor.allow_tags = True


class PurchaseReport(Transactions):
    class Meta:
        proxy = True
        verbose_name = 'Purchase Report'
        verbose_name_plural = 'Purchase Report'

class PurchaseReportAdmin(admin.ModelAdmin):
    model = Transactions
    list_display = ('date', 'amount', 'transaction_neighbor_first_name', 'transaction_neighbor_last_name', 'transaction_type', 'transaction_community')

    list_filter = ('date', AmountListFilter,)
    search_fields = ['wallet__neighbor__user__first_name', 'wallet__neighbor__user__last_name', 'wallet__neighbor__user__email', 'amount']

    ordering = ('-date',)

    fields = ('transaction_neighbor', 'date', 'title', 'stripe_paid', 'transaction_type', 'amount', 'stripe_id', 'failure_code', 'failure_message',)
    readonly_fields = ('transaction_neighbor', 'date',)

    actions = [export_xlsx, export_csv]

    def queryset(self, request):
        return self.model.objects.filter(stripe_paid=True)

    def transaction_neighbor(self, obj):
        return u'<a href="/admin/neighbor/neighbor/%d/">%s</a>' % (obj.wallet.neighbor.id, obj.wallet.neighbor)
    transaction_neighbor.short_description = 'Neighbor'
    transaction_neighbor.allow_tags = True

    def transaction_neighbor_first_name(self, obj):
        return u'<a href="/admin/neighbor/neighbor/%d/">%s</a>' % (obj.wallet.neighbor.id, obj.wallet.neighbor.first_name)
    transaction_neighbor_first_name.short_description = 'First Name'
    transaction_neighbor_first_name.allow_tags = True
    transaction_neighbor_first_name.admin_order_field = 'wallet__neighbor__user__first_name'

    def transaction_neighbor_last_name(self, obj):
        return u'<a href="/admin/neighbor/neighbor/%d/">%s</a>' % (obj.wallet.neighbor.id, obj.wallet.neighbor.last_name)
    transaction_neighbor_last_name.short_description = 'Last Name'
    transaction_neighbor_last_name.allow_tags = True
    transaction_neighbor_last_name.admin_order_field = 'wallet__neighbor__user__last_name'

    def transaction_community(self, obj):
        return u'<a href="/admin/community/community/%d/">%s</a>' % (obj.wallet.neighbor.community.id, obj.wallet.neighbor.community)
    transaction_community.short_description = 'Community'
    transaction_community.allow_tags = True
    transaction_community.admin_order_field = 'wallet__neighbor__community'

    # removes the "add transaction" button
    def has_add_permission(self, request):
        return False


admin.site.register(Neighbor, NeighborAdmin)
admin.site.register(CalendarEvent, CalendarEventAdmin)
admin.site.register(Transactions, TransactionsAdmin)
admin.site.register(PurchaseReport, PurchaseReportAdmin)