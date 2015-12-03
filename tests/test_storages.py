# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from django.conf import settings
from django.core.files.base import ContentFile
from django.test import TestCase

from boto import connect_s3
from moto import mock_s3

from staticgen.staticgen_storages import StaticgenDefaultFilesStorage, StaticgenStaticFilesStorage


class TestStaticgenStorage(TestCase):

    @mock_s3
    def _upload(self, storage, folder):
        # setUp
        connection = connect_s3()
        connection.create_bucket(settings.AWS_STORAGE_BUCKET_NAME)

        # upload a file
        file_name = 's3dummyfile.txt'
        file_text = 'django-staticgen is awesome!'
        file_content = ContentFile(file_text)
        storage.save(file_name, file_content)

        # confirm it was uploaded
        temp_file = storage.open(file_name, 'r')
        self.assertEqual(temp_file.read(), file_text)

        # check folder
        expected_path = '{folder}/{file_name}'.format(folder=folder, file_name=file_name)
        self.assertEqual(temp_file.key.name, expected_path)

        temp_file.close()

    def test_s3_defaultfiles_storage(self):
        self._upload(StaticgenDefaultFilesStorage(), settings.AWS_S3_DEFAULTFILES_LOCATION)

    def test_s3_staticfiles_storage(self):
        self._upload(StaticgenStaticFilesStorage(), settings.AWS_S3_STATICFILES_LOCATION)
