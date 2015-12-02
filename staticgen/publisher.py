# -*- coding: utf-8 -*-

from __future__ import unicode_literals

import logging
import os
import time
from multiprocessing.pool import ThreadPool

from django.core.files.base import ContentFile
from django.test import Client
from django.utils.encoding import force_text
from django.utils.translation import ugettext_lazy as _

from boto import connect_s3

from .conf import settings
from .helpers import get_static_site_domain
from .models import LogEntry, Page
from .signals import publishing_complete
from .status import is_redirect, is_success

try:
    from urllib.parse import urlparse
except ImportError:  # pragma: no cover
    # Python 2.X
    from urlparse import urlparse

logger = logging.getLogger('staticgen')


class StaticgenPublisher(object):
    model = Page

    def __init__(self):
        self.client = None
        self.connection = None
        self.bucket = None
        self.updated_paths = []
        self.deleted_paths = []

    def get_client(self):
        if self.client is None:
            self.client = Client(SERVER_NAME=get_static_site_domain())
        return self.client

    def get_page(self, path):
        client = self.get_client()
        extra_kwargs = {
            'HTTP_X_STATICGEN_PUBLISHER': True
        }
        return client.get(path, **extra_kwargs)

    def get_connection(self):
        if self.connection is None:
            self.connection = connect_s3(
                settings.AWS_ACCESS_KEY_ID,
                settings.AWS_SECRET_ACCESS_KEY
            )
        return self.connection

    def get_bucket_name(self):
        return settings.STATICGEN_BUCKET_NAME

    def get_bucket(self):
        if self.bucket is None:
            connection = self.get_connection()
            bucket_name = self.get_bucket_name()
            self.bucket = connection.get_bucket(bucket_name)
        return self.bucket

    def get_queryset(self, pending=False, changed=False, obj=None):
        queryset = self.model._default_manager.all()
        queryset = queryset.on_site()
        queryset = queryset.exclude(publisher_state=self.model.PUBLISHER_STATE_DELETE)

        if obj is not None:
            queryset = queryset.filter(pk=obj.pk)
        elif pending and not changed:
            queryset = queryset.pending()
        elif changed and not pending:
            queryset = queryset.changed()
        elif pending and changed:
            queryset = queryset.pending_and_changed()

        return queryset

    def get_output_path(self, path):
        if path.endswith('/'):
            path = os.path.join(path, 'index.html')
        return path[1:] if path.startswith('/') else path

    def log_error(self, page, message):
        self.log_action(page, message)
        page.publisher_state = self.model.PUBLISHER_STATE_ERROR
        page.save()

        message = _('Page: {path} - {message}').format(
            path=page.path, message=message)
        logger.error(message)

    def log_success(self, page, message):
        self.log_action(page, message)
        page.publisher_state = self.model.PUBLISHER_STATE_PUBLISHED
        page.save()

        message = _('Page: {path} - {message}').format(
            path=page.path, message=message)
        logger.info(message)

    def log_action(self, page, message):
        LogEntry.objects.log_action(
            change_message=message,
            page_id=page.pk,
        )

    def delete_removed(self):
        bucket = self.get_bucket()
        deleted_pages = self.model._default_manager.deleted()
        to_delete = []

        for page in deleted_pages:
            output_path = self.get_output_path(page.path)
            to_delete.append(output_path)

            self.deleted_paths.append((page.path, output_path))

        if to_delete:
            key_chunks = []
            for i in range(0, len(to_delete), 100):
                key_chunks.append(to_delete[i:i+100])
            for chunk in key_chunks:
                bucket.delete_keys(chunk)

            message = _('Successfully deleted {deleted_count} pages.').format(
                deleted_count=len(to_delete))
            logger.info(message)

            # finally delete records from the database
            deleted_pages.delete()

    def pre_publish(self, sync_pages=True):
        # start timer
        self.start_time = time.time()

    def post_publish(self):
        # delete pages that have been marked for deletion
        self.delete_removed()

        elapsed_time = time.time() - self.start_time
        message = _('Publishing completed successfully. {updated_count} page(s) was updated, '
                    'deleted {deleted_count} page(s), in {elapsed_time:.2f} seconds.').format(
            updated_count=len(self.updated_paths),  deleted_count=len(self.deleted_paths),
            elapsed_time=elapsed_time)

        publishing_complete.send(
            sender=self.__class__,
            updated_paths=self.updated_paths,
            deleted_paths=self.deleted_paths
        )

        LogEntry.objects.log_action(message)
        logger.info(message)

    def handle_page_redirect(self, page, response, key):
        has_changed = False

        redirect_url = response['Location']
        redirect_url = urlparse(redirect_url)
        redirect_response = self.get_page(redirect_url.path)

        if not is_success(redirect_response.status_code):  # pragma: no cover
            message = _('Couldn\'t retrieve redirection page: {path} - Code: {code}').format(
                path=redirect_url.path, code=redirect_response.status_code
            )
            self.log_error(page, message)
            return page, has_changed

        # don't re-upload identical redirects
        if key.exists() and redirect_url.path == key.get_redirect():
            return page, has_changed

        key.set_redirect(redirect_url.path)
        key.make_public()
        has_changed = True
        message = _('Added redirection from "{path}" to "{redirect}"').format(
            path=page.path, redirect=redirect_url.path)
        self.log_success(page, message)

        return page, has_changed

    def handle_page_upload(self, page, response, key):
        has_changed = False

        temp_file = ContentFile(response.content)
        local_md5, b64 = key.compute_md5(temp_file)

        etag = key.etag or ''  # If key is new, there's no etag yet
        remote_md5 = etag.strip('"')  # for some weird reason, etags are quoted

        # force publish if page is marked as changed
        if not remote_md5 == local_md5 or page.has_changed:
            has_changed = True
            key.set_contents_from_file(temp_file, policy='public-read')
            message = _('The content was successfully published.')
            self.log_success(page, message)

        temp_file.close()
        return page, has_changed

    def _upload(self, page):
        has_changed = False

        response = self.get_page(page.path)
        if not is_success(response.status_code) \
                and not is_redirect(response.status_code):  # pragma: no cover

            message = _('Error retrieving page: {path} - Code: {code}').format(
                path=page.path, code=response.status_code)

            self.log_error(page, message)
            return page

        bucket = self.get_bucket()
        output_path = self.get_output_path(page.path)

        key = bucket.get_key(output_path) or bucket.new_key(output_path)
        key.content_type = response['Content-Type']

        if is_redirect(response.status_code):
            page, has_changed = self.handle_page_redirect(page, response, key)

        if is_success(response.status_code):
            page, has_changed = self.handle_page_upload(page, response, key)

        if has_changed:
            self.updated_paths.append((page.path, output_path))

        if not has_changed:  # pragma: no cover
            message = _('The content has not changed.')
            self.log_success(page, message)

        return page

    def upload_to_s3(self, page):
        try:
            page = self._upload(page)
        except Exception as e:  # pragma: no cover
            message = _('Error publishing page: {path} - Error: {error}').format(
                path=page.path, error=force_text(e))
            self.log_error(page, message)
        return page

    def publish(self, pending=False, changed=False, obj=None, sync=False):
        self.pre_publish()

        if sync:
            self.model.objects.sync()

        queryset = self.get_queryset(pending=pending, changed=changed, obj=obj)

        if not settings.STATICGEN_MULTITHREAD:
            for page in queryset:
                self.upload_to_s3(page)
        else:
            pool = ThreadPool(processes=10)
            pool.map(self.upload_to_s3, queryset, chunksize=5)

        self.post_publish()
