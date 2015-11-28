# -*- coding: utf-8 -*-

from django.conf import settings
from django.contrib.sites.models import Site

from boto import connect_s3


class StaticgenSitemap(object):

    def get_website_endpoint(self):
        connection = connect_s3(
            settings.AWS_ACCESS_KEY_ID,
            settings.AWS_SECRET_ACCESS_KEY
        )
        bucket = connection.get_bucket(settings.AWS_STORAGE_BUCKET_NAME)
        return bucket.get_website_endpoint()

    def get_urls(self, page=1, site=None, protocol=None):
        website_endpoint = self.get_website_endpoint()
        site = Site(domain=website_endpoint, name='Amazon S3 Website Endpoint')
        return super(StaticgenSitemap, self).get_urls(page=page, site=site, protocol=protocol)


def override_sitemaps_domain(sitemaps):
    staticgen_sitemaps = {}
    for section, site in sitemaps.items():
        cls_name = 'Staticgen{name}'.format(name=site.__name__)
        staticgen_sitemaps[section] = type(cls_name, (StaticgenSitemap, site), {})
    return staticgen_sitemaps
