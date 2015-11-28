# -*- coding: utf-8 -*-

from __future__ import unicode_literals

import logging
import time

from django.contrib.sites.models import Site
from django.db import models
from django.db.models import Q
from django.utils.encoding import python_2_unicode_compatible
from django.utils.translation import ugettext_lazy as _

from .conf import settings
from .staticgen_pool import staticgen_pool

try:
    from urllib.parse import urlparse
except ImportError:  # pragma: no cover
    # Python 2.X
    from urlparse import urlparse

logger = logging.getLogger('staticgen')


class PageQuerySet(models.QuerySet):

    def changed(self):
        return self.filter(publisher_state=self.model.PUBLISHER_STATE_CHANGED)

    def pending(self):
        return self.filter(publisher_state=self.model.PUBLISHER_STATE_DEFAULT)

    def pending_and_changed(self):
        return self.filter(
            Q(publisher_state=self.model.PUBLISHER_STATE_DEFAULT) |
            Q(publisher_state=self.model.PUBLISHER_STATE_CHANGED)
        )

    def published(self):
        return self.filter(publisher_state=self.model.PUBLISHER_STATE_PUBLISHED)

    def on_site(self, site_id=settings.SITE_ID):
        return self.filter(site__id=site_id)

    def deleted(self):
        return self.filter(publisher_state=self.model.PUBLISHER_STATE_DELETE)


class PageManager(models.Manager):
    use_in_migrations = True

    def get_queryset(self):
        return PageQuerySet(self.model, using=self._db)

    def changed(self):
        return self.get_queryset().changed()

    def pending(self):
        return self.get_queryset().pending()

    def pending_and_changed(self):
        return self.get_queryset().pending_and_changed()

    def published(self):
        return self.get_queryset().published()

    def deleted(self):
        return self.get_queryset().deleted()

    def on_site(self, site_id=settings.SITE_ID):
        return self.get_queryset().on_site(site_id=site_id)

    def get_or_create_url(self, url, site_id=settings.SITE_ID):
        parse_result = urlparse(url)
        obj, created = self.model.objects.get_or_create(
            site_id=site_id,
            path=parse_result.path
        )
        return obj, created

    def sync(self, site_id=settings.SITE_ID):
        start_time = time.time()

        urls = []
        urls.extend(staticgen_pool.get_urls())
        urls = list(set(urls))
        urls.sort()

        urls_to_keep = []
        created_count = 0

        for url in urls:
            url, created = self.get_or_create_url(url, site_id=site_id)
            urls_to_keep.append(url.pk)
            if created:
                created_count += 1

        deleted_count = self.model.objects \
            .on_site(site_id=site_id) \
            .exclude(pk__in=urls_to_keep) \
            .update(publisher_state=self.model.PUBLISHER_STATE_DELETE)

        elapsed_time = time.time() - start_time
        message = _('Syncing URLs completed successfully. {created_count} page(s) was added, '
                    'deleted {deleted_count} page(s), in {elapsed_time:.2f} seconds.').format(
            created_count=created_count, deleted_count=deleted_count, elapsed_time=elapsed_time)

        LogEntry.objects.log_action(message)
        logger.info(message)

        return self.model.objects.on_site(site_id=site_id)


@python_2_unicode_compatible
class Page(models.Model):
    PUBLISHER_STATE_DEFAULT = 0
    PUBLISHER_STATE_CHANGED = 1
    PUBLISHER_STATE_PUBLISHED = 2
    PUBLISHER_STATE_ERROR = 3
    PUBLISHER_STATE_DELETE = 4

    PUBLISHER_STATES = (
        (PUBLISHER_STATE_DEFAULT, _('Pending')),
        (PUBLISHER_STATE_CHANGED, _('Changed')),
        (PUBLISHER_STATE_PUBLISHED, _('Published')),
        (PUBLISHER_STATE_ERROR, _('Error')),
        (PUBLISHER_STATE_DELETE, _('Deleted'))
    )

    site = models.ForeignKey(Site, verbose_name=_('Site'))
    path = models.CharField(_('URL'), max_length=255)
    publisher_state = models.SmallIntegerField(
        _('State'), choices=PUBLISHER_STATES, default=PUBLISHER_STATE_DEFAULT,
        editable=False, db_index=True)
    updated_at = models.DateTimeField(auto_now=True)
    objects = PageManager()

    class Meta:
        verbose_name = _('page')
        verbose_name_plural = _('pages')
        ordering = ('path', )
        unique_together = ('site', 'path')

    def __str__(self):
        return self.path

    @property
    def has_changed(self):
        return self.publisher_state == self.PUBLISHER_STATE_CHANGED


class LogEntryManager(models.Manager):
    use_in_migrations = True

    def log_action(self, change_message, page_id=None, site_id=settings.SITE_ID):
        obj = self.model(
            change_message=change_message,
            page_id=page_id,
            site_id=site_id,
        )
        obj.save()


@python_2_unicode_compatible
class LogEntry(models.Model):
    site = models.ForeignKey(Site, verbose_name=_('Site'))
    page = models.ForeignKey(Page, blank=True, null=True, on_delete=models.CASCADE)
    change_message = models.TextField(_('change message'))
    action_time = models.DateTimeField(_('action time'), auto_now=True)

    objects = LogEntryManager()

    class Meta:
        verbose_name = _('log entry')
        verbose_name_plural = _('log entries')
        ordering = ('-action_time',)

    def __str__(self):
        return self.change_message
