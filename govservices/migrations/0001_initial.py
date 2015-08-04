# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='SubService',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('cat_id', models.CharField(max_length=512)),
                ('desc', models.TextField()),
                ('name', models.CharField(max_length=512)),
                ('info_url', models.CharField(max_length=512, null=True, blank=True)),
                ('primary_audience', models.CharField(max_length=512, null=True, blank=True)),
            ],
        ),
    ]
