# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from django.contrib.sites.models import Site

from .helpers import get_static_site_domain


def staticgen_publisher(request):
    context = {}

    is_publishing = request.META.get('HTTP_X_STATICGEN_PUBLISHER', False)
    context['STATICGEN_IS_PUBLISHING'] = is_publishing

    current_site = Site.objects.get_current()
    context['STATICGEN_BASE_URL'] = get_static_site_domain() \
        if is_publishing else current_site.domain

    return context
