# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('metadata', '0004_auto_20150728_1500'),
    ]

    operations = [
        migrations.AlterField(
            model_name='resource',
            name='_hash',
            field=models.CharField(max_length=512, null=True, db_column=b'hash', blank=True),
        ),
        migrations.AlterField(
            model_name='resource',
            name='contenttype',
            field=models.CharField(max_length=512, null=True, blank=True),
        ),
        migrations.AlterField(
            model_name='resource',
            name='host',
            field=models.CharField(max_length=512, null=True, blank=True),
        ),
        migrations.AlterField(
            model_name='resource',
            name='url',
            field=models.CharField(max_length=1024),
        ),
    ]
