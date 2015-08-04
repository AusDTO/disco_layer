# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('govservices', '0014_auto_20150630_0235'),
    ]

    operations = [
        migrations.AlterField(
            model_name='service',
            name='src_id',
            field=models.CharField(default='DEFAULT VALUE', max_length=256),
            preserve_default=False,
        ),
    ]
