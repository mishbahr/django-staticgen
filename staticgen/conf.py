# -*- coding: utf-8 -*-

from django.conf import settings  # noqa
from django.utils.translation import ugettext_lazy as _  # noqa

from appconf import AppConf


class StaticgenConf(AppConf):
    SITEMAP_URL = None
    FAIL_SILENTLY = True
    MULTITHREAD = True
    BUCKET_NAME = getattr(settings, 'AWS_STORAGE_BUCKET_NAME', '')
    STATIC_SITE_DOMAIN = None

    class Meta:
        prefix = 'staticgen'
