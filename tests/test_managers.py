#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from django.conf import settings
from django.contrib.sites.models import Site
from django.test import TestCase

from staticgen.models import LogEntry, Page


class TestStaticgenLogEntryManager(TestCase):
    change_message = 'Something changed'

    def setUp(self):
        self.page = Page.objects.create(path='/', site_id=settings.SITE_ID)
        self.log_entry = LogEntry.objects.log_action(self.change_message, page_id=self.page.id)

    def test_log_action_change_message(self):
        log = LogEntry.objects.all()[0]
        self.assertEqual(self.change_message, log.change_message)

    def test_log_action_site_id(self):
        log = LogEntry.objects.all()[0]
        self.assertEqual(settings.SITE_ID, log.site_id)

    def test_log_action_page(self):
        log = LogEntry.objects.all()[0]
        self.assertEqual(self.page, log.page)


class TestStaticgenPageManager(TestCase):

    def setUp(self):
        site2 = Site.objects.create(name='Site 2', domain='acme.com')

        Page.objects.create(path='/page1/', site_id=settings.SITE_ID)
        Page.objects.create(
            path='/page2/', site_id=settings.SITE_ID,
            publisher_state=Page.PUBLISHER_STATE_CHANGED)
        Page.objects.create(
            path='/page3/', site_id=settings.SITE_ID,
            publisher_state=Page.PUBLISHER_STATE_PUBLISHED)
        Page.objects.create(
            path='/page4/', site_id=settings.SITE_ID,
            publisher_state=Page.PUBLISHER_STATE_ERROR)
        Page.objects.create(
            path='/page5/', site=site2,
            publisher_state=Page.PUBLISHER_STATE_DELETE
        )

    def test_page_manager_default(self):
        self.failUnlessEqual(Page.objects.all().count(), 5)

    def test_page_manager_changed(self):
        self.failUnlessEqual(Page.objects.changed().count(), 1)

    def test_page_manager_pending(self):
        self.failUnlessEqual(Page.objects.pending().count(), 1)

    def test_page_manager_pending_and_changed(self):
        self.failUnlessEqual(Page.objects.pending_and_changed().count(), 2)

    def test_page_manager_published(self):
        self.failUnlessEqual(Page.objects.published().count(), 1)

    def test_page_manager_deleted(self):
        self.failUnlessEqual(Page.objects.deleted().count(), 1)

    def test_page_manager_on_site(self):
        self.failUnlessEqual(Page.objects.on_site().count(), 4)

    def test_page_manager_get_or_create_url(self):
        full_url = 'http://example.com/test-page?query=1'
        page, created = Page.objects.get_or_create_url(full_url)

        self.assertEqual(page.path, '/test-page')
        self.assertEqual(page.site_id, settings.SITE_ID)
        self.assertTrue(created, '')


class TestStaticgenPageManagerSync(TestCase):

    def setUp(self):
        Page.objects.create(path='/page1/', site_id=settings.SITE_ID)
        Page.objects.create(path='/page2/', site_id=settings.SITE_ID)
        Page.objects.create(path='/page3/', site_id=settings.SITE_ID)

        Page.objects.sync()

    def test_log_action(self):
        # checking log entry are added w/ the correct SITE_ID
        log = LogEntry.objects.all()[0]
        self.assertEqual(log.site_id, settings.SITE_ID)

    def test_page_deletion(self):
        # pages we created during setUp should be marked as deleted
        self.assertEqual(Page.objects.deleted().count(), 3)

    def test_page_pending_publish(self):
        # See example app and its fixtures for page data
        self.assertEqual(Page.objects.pending().count(), 16)

    def test_page_on_site(self):
        # All pages should belong to SITE_ID in the settings
        self.assertEqual(Page.objects.on_site().count(), 19)
