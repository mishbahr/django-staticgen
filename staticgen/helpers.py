# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from boto import connect_s3

from .conf import settings


def get_static_site_domain():
    static_site_domain = settings.STATICGEN_STATIC_SITE_DOMAIN
    if static_site_domain is None:
        connection = connect_s3(
            settings.AWS_ACCESS_KEY_ID,
            settings.AWS_SECRET_ACCESS_KEY
        )
        bucket = connection.get_bucket(settings.AWS_STORAGE_BUCKET_NAME)
        static_site_domain = bucket.get_website_endpoint()
    return static_site_domain
