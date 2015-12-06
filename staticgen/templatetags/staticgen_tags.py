# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from django import template
from django.core.urlresolvers import Resolver404, resolve, reverse

register = template.Library()


@register.simple_tag(takes_context=True)
def routable_pageurl(context, page=1, page_kwarg='page'):
    request = context['request']

    try:
        match = resolve(request.path_info)
    except Resolver404:  # pragma: no cover
        pass
    else:
        if match.namespace:
            namespace = '{0}:'.format(match.namespace)
        else:
            namespace = ''

        current_url = '{namespace}{url_name}'.format(
            namespace=namespace, url_name=match.url_name)

        match.kwargs[page_kwarg] = page
        return reverse(current_url, args=match.args, kwargs=match.kwargs)

    return ''
