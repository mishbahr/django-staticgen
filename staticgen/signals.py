# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from django.dispatch import Signal


# Publishing completed successfully.
publishing_complete = Signal(providing_args=['updated_paths', 'deleted_paths', ])
