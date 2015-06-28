# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('govservices', '0009_auto_20150628_1318'),
    ]

    operations = [
        migrations.AddField(
            model_name='service',
            name='json_filename',
            field=models.CharField(max_length=512, null=True, blank=True),
        ),
        migrations.AddField(
            model_name='service',
            name='org_acronym',
            field=models.CharField(max_length=64, null=True, blank=True),
        ),
    ]
