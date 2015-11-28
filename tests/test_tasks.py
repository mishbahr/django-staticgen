#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from django.conf import settings
from django.test import TestCase

from boto import connect_s3
from moto import mock_s3

from staticgen.models import Page
from staticgen.tasks import publish_pages, publish_pending, sync_pages, publish_changed


class TestCeleryTasks(TestCase):

    def test_sync_pages(self):
        # this should should add 16 pages to database
        sync_pages()
        self.assertEqual(Page.objects.all().count(), 16)

    @mock_s3
    def test_publish_pending(self):
        # setUp
        connection = connect_s3()
        connection.create_bucket(settings.AWS_STORAGE_BUCKET_NAME)

        Page.objects.sync()

        # there should be 16 pending publish pages in the database
        self.assertEqual(Page.objects.pending().count(), 16)

        # actual test - this should publish all 16  pages
        publish_pending()

        # there should no more pending pages.
        self.assertEqual(Page.objects.pending().count(), 0)


    @mock_s3
    def test_publish_changed(self):
        # setUp
        connection = connect_s3()
        connection.create_bucket(settings.AWS_STORAGE_BUCKET_NAME)
        Page.objects.sync()  # adds 16 pages to database

        # mark 5 pages as changed.
        page_ids = Page.objects.values_list('pk', flat=True)[:5]
        Page.objects.filter(pk__in=page_ids).update(publisher_state=Page.PUBLISHER_STATE_CHANGED)

        # there should be 5 pages - marked as changed
        self.assertEqual(Page.objects.changed().count(), 5)

        # actual test - this should publish 5 pages marked as changed.
        publish_changed()

        # there should no more unpublished pages
        self.assertEqual(Page.objects.changed().count(), 0)

    @mock_s3
    def test_publish_pages(self):
        # setUp
        connection = connect_s3()
        connection.create_bucket(settings.AWS_STORAGE_BUCKET_NAME)
        Page.objects.sync()  # adds 16 pages to database

        # actual test - this should publish/update all registered pages
        publish_pages()

        # Every page should be published – 16 pages in total
        self.assertEqual(Page.objects.published().count(), 16)


