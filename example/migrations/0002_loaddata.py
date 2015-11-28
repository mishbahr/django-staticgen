# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from django.core.management import call_command
from django.db import migrations


def loadfixture(apps, schema_editor):
    call_command('loaddata', 'initial_data.json')


class Migration(migrations.Migration):

    dependencies = [
        ('example', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(loadfixture),
    ]
