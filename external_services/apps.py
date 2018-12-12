from django.apps import AppConfig
from django.utils.translation import ugettext_lazy as _


class ServicesConfig(AppConfig):
    name = 'external_services'
    verbose_name = _('External Services')

    def ready(self):
        import external_services.signals
