# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('spiderbucket', '0002_auto_20150618_1342'),
    ]

    operations = [
        migrations.AlterField(
            model_name='page',
            name='depth',
            field=models.IntegerField(null=True, blank=True),
        ),
        migrations.AlterField(
            model_name='page',
            name='port',
            field=models.IntegerField(null=True, blank=True),
        ),
    ]
