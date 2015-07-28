# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('metadata', '0002_auto_20150728_1312'),
    ]

    operations = [
        migrations.AddField(
            model_name='resource',
            name='_hash',
            field=models.CharField(max_length=255, null=True, db_column=b'hash', blank=True),
        ),
    ]
