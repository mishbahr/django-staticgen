from django.apps import AppConfig
from django.utils.translation import ugettext_lazy as _


class StaticgenAppConfig(AppConfig):
    name = 'staticgen'
    verbose_name = _('StaticGen')
