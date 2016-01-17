# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from django.contrib.sites.models import Site

from .helpers import get_static_site_domain


def staticgen_publisher(request):
    context = {}

    is_publishing = request.META.get('HTTP_X_STATICGEN_PUBLISHER', False)
    context['STATICGEN_IS_PUBLISHING'] = is_publishing

    current_site = Site.objects.get_current()

    base_url = current_site.domain
    if is_publishing:
        base_url = get_static_site_domain()

    context['STATICGEN_BASE_URL'] = base_url

    return context
