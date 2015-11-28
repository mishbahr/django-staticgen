#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from django.conf import settings
from django.core.management import call_command
from django.test import TestCase

from boto import connect_s3
from mock import patch
from moto import mock_s3

from staticgen.models import Page


class TestCommands(TestCase):

    @mock_s3
    def test_publish(self):
        # setUp
        connection = connect_s3()
        connection.create_bucket(settings.AWS_STORAGE_BUCKET_NAME)
        bucket = connection.get_bucket(settings.AWS_STORAGE_BUCKET_NAME)

        # actual test
        call_command('staticgen_publish')

        # Every page should be published – 16 pages in total
        self.assertEqual(Page.objects.published().count(), 16)

        # 16 pages should have been uploaded to S3 bucket
        keys = [s3_key.name for s3_key in bucket.list()]
        self.assertTrue(len(keys), 16)    \

    @patch('staticgen.tasks.publish_pages.delay')
    def test_publish_async(self, mocked_task):
        call_command('staticgen_publish_async')
        # test celery task was called
        self.assertTrue(mocked_task.called)


