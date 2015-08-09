# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='WebDocument',
            fields=[
                ('url', models.TextField(serialize=False, primary_key=True)),
                ('host', models.CharField(max_length=255, null=True, blank=True)),
                ('document', models.BinaryField(null=True, blank=True)),
                ('lastfetchdatetime', models.DateTimeField(null=True, db_column='lastFetchDateTime', blank=True)),
                ('nextfetchdatetime', models.DateTimeField(null=True, db_column='nextFetchDateTime', blank=True)),
                ('path', models.TextField(null=True, blank=True)),
                ('port', models.IntegerField(null=True, blank=True)),
                ('protocol', models.CharField(max_length=255, null=True, blank=True)),
                ('httpcode', models.IntegerField(null=True, db_column='httpCode', blank=True)),
                ('contenttype', models.CharField(max_length=255, null=True, db_column='contentType', blank=True)),
                ('statedata', models.TextField(null=True, db_column='stateData', blank=True)),
                ('fetchstatus', models.CharField(max_length=255, null=True, db_column='fetchStatus', blank=True)),
                ('fetched', models.NullBooleanField()),
                ('outlinks', models.TextField(null=True, blank=True)),
                ('_hash', models.CharField(max_length=255, null=True, db_column='hash', blank=True)),
                ('version', models.IntegerField(null=True, blank=True)),
                ('created_at', models.DateTimeField()),
                ('updated_at', models.DateTimeField()),
            ],
            options={
                'db_table': 'webDocuments',
                'managed': False,
            },
        ),
    ]
