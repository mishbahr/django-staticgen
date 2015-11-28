# -*- coding: utf-8 -*-

from __future__ import unicode_literals


def staticgen_publisher(request):
    return {
        'is_publishing': request.META.get('HTTP_X_STATICGEN_PUBLISHER', False),
    }
