# -*- coding: utf-8 -*-

from __future__ import unicode_literals

import logging

from django.core.urlresolvers import resolve, reverse
from django.shortcuts import resolve_url
from django.test import Client
from django.utils import translation
from django.utils.translation import ugettext_lazy as _

from .conf import settings
from .exceptions import StaticgenError
from .helpers import get_static_site_domain
from .status import is_success

logger = logging.getLogger('staticgen')


class StaticgenView(object):
    is_paginated = False

    def __init__(self, *args, **kwargs):
        super(StaticgenView, self).__init__(*args, **kwargs)
        self.client = Client(SERVER_NAME=get_static_site_domain())

    def items(self):
        return []

    def log_error(self, message):
        logger.error(message)
        if not settings.STATICGEN_FAIL_SILENTLY:
            raise StaticgenError(message)

    def url(self, item):
        return resolve_url(item)

    def _get_context_data(self, response):
        for key in ('context', 'context_data',):
            context = getattr(response, key, None)
            if context:
                return context

    def _get_paginator(self, url):
        response = self.client.get(url)
        if not is_success(response.status_code):  # pragma: no cover
            message = _('Error retrieving: {url} - Code: {code}').format(
                url=url, code=response.status_code)
            self.log_error(message)
        else:
            context_data = self._get_context_data(response)
            if context_data:
                try:
                    return context_data['paginator'], context_data['is_paginated']
                except KeyError:  # pragma: no cover
                    pass
        return None, False

    def _urls(self, page):
        urls = []

        url = self.url(page)
        urls.append(url)  # first page

        if self.is_paginated:
            paginator, is_paginated = self._get_paginator(url)
            if paginator is not None and is_paginated:
                page_range = paginator.page_range
                match = resolve(url)
                for page_num in page_range:
                    kwargs = match.kwargs.copy()
                    kwargs.update({
                        'page': page_num
                    })
                    urls.append(reverse(match.view_name, args=match.args, kwargs=kwargs))

        return urls

    def get_urls(self):
        urls = []
        for page in self.items():
            if getattr(self, 'i18n', False):
                current_lang_code = translation.get_language()
                for lang_code, lang_name in settings.LANGUAGES:
                    translation.activate(lang_code)
                    urls += self._urls(page)
                translation.activate(current_lang_code)
            else:
                urls += self._urls(page)

        urls = list(set(urls))
        urls.sort()
        return urls
