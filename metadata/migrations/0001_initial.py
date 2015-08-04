# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Page',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('url', models.CharField(max_length=256)),
                ('protocol', models.CharField(max_length=6, null=True, blank=True)),
                ('host', models.CharField(max_length=256, null=True, blank=True)),
                ('port', models.IntegerField(null=True, blank=True)),
                ('path', models.TextField(null=True, blank=True)),
                ('depth', models.IntegerField(null=True, blank=True)),
                ('fetched', models.NullBooleanField()),
                ('status', models.CharField(max_length=256, null=True, blank=True)),
                ('lastFetchDateTime', models.DateTimeField(null=True, blank=True)),
                ('nextFetchDateTime', models.DateTimeField(null=True, blank=True)),
                ('document', models.TextField(null=True, blank=True)),
            ],
        ),
    ]
