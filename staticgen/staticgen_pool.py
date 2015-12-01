# -*- coding: utf-8 -*-

from __future__ import unicode_literals

import logging

from django.utils.translation import ugettext_lazy as _

from .conf import settings
from .exceptions import StaticgenError

try:
    from importlib import import_module
except ImportError:  # pragma: no cover
    # Python < 2.7
    from django.utils.importlib import import_module


logger = logging.getLogger('staticgen')


class StaticgenPool(object):
    def __init__(self):
        self._discovered = False
        self.modules = {}

    def log_error(self, message):
        logger.error(message)
        if not settings.STATICGEN_FAIL_SILENTLY:
            raise StaticgenError(message)

    def register(self, cls):
        from .staticgen_views import StaticgenView
        if not issubclass(cls, StaticgenView):
            message = _('Staticgen Views must inherit '
                        '"staticgen.staticgen_views.StaticgenView", '
                        '{cls} does not').format(cls=cls)
            self.log_error(message)
            return False  # pragma: no cover

        name = '{module}.{name}'.format(module=cls.__module__, name=cls.__name__)
        if name in self.modules.keys():
            message = _('"{name}" a Staticgen view with this name '
                        'is already registered'.format(name=name))
            self.log_error(message)
            return False  # pragma: no cover

        self.modules[name] = cls()

    def autodiscover(self):
        if self._discovered:  # pragma: no cover
            return

        for app in settings.INSTALLED_APPS:
            staticgen_views = app + '.staticgen_views'
            try:
                import_module(staticgen_views)
            except ImportError:
                pass
        self._discovered = True

    def get_urls(self):
        urls = []
        for name, module in self.modules.items():
            urls.extend(module.get_urls())

        urls = list(set(urls))
        urls.sort()
        return urls

staticgen_pool = StaticgenPool()
