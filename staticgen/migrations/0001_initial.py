# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('sites', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='LogEntry',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('change_message', models.TextField(verbose_name='change message')),
                ('action_time', models.DateTimeField(auto_now=True, verbose_name='action time')),
            ],
            options={
                'ordering': ('-action_time',),
                'verbose_name': 'log entry',
                'verbose_name_plural': 'log entries',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Page',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('path', models.CharField(max_length=255, verbose_name='URL')),
                ('publisher_state', models.SmallIntegerField(default=0, verbose_name='State', db_index=True, editable=False, choices=[(0, 'Pending'), (1, 'Changed'), (2, 'Published'), (3, 'Error'), (4, 'Deleted')])),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('site', models.ForeignKey(verbose_name='Site', to='sites.Site')),
            ],
            options={
                'ordering': ('path',),
                'verbose_name': 'page',
                'verbose_name_plural': 'pages',
            },
            bases=(models.Model,),
        ),
        migrations.AlterUniqueTogether(
            name='page',
            unique_together=set([('site', 'path')]),
        ),
        migrations.AddField(
            model_name='logentry',
            name='page',
            field=models.ForeignKey(blank=True, to='staticgen.Page', null=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='logentry',
            name='site',
            field=models.ForeignKey(verbose_name='Site', to='sites.Site'),
            preserve_default=True,
        ),
    ]
