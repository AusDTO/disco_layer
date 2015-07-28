# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('metadata', '0003_resource__hash'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='resource',
            name='document',
        ),
        migrations.RemoveField(
            model_name='resource',
            name='fetched',
        ),
        migrations.RemoveField(
            model_name='resource',
            name='nextFetchDateTime',
        ),
        migrations.RemoveField(
            model_name='resource',
            name='status',
        ),
        migrations.AddField(
            model_name='resource',
            name='contenttype',
            field=models.CharField(max_length=256, null=True, blank=True),
        ),
    ]
