# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('govservices', '0005_service'),
    ]

    operations = [
        migrations.AlterField(
            model_name='service',
            name='src_id',
            field=models.CharField(max_length=256, null=True, blank=True),
        ),
    ]
