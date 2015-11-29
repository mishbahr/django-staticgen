# -*- coding: utf-8 -*-

from django.contrib.sites.models import Site

from .helpers import get_static_site_domain


class StaticgenSitemap(object):

    def get_urls(self, page=1, site=None, protocol=None):
        site = Site(domain=get_static_site_domain(), name='Static Site Domain')
        return super(StaticgenSitemap, self).get_urls(page=page, site=site, protocol=protocol)


def override_sitemaps_domain(sitemaps):
    staticgen_sitemaps = {}
    for section, site in sitemaps.items():
        cls_name = 'Staticgen{name}'.format(name=site.__name__)
        staticgen_sitemaps[section] = type(cls_name, (StaticgenSitemap, site), {})
    return staticgen_sitemaps
