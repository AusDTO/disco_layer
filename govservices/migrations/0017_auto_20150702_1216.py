# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('govservices', '0016_auto_20150702_1215'),
    ]

    operations = [
        migrations.AlterField(
            model_name='dimension',
            name='dim_id',
            field=models.CharField(default=1, max_length=512),
            preserve_default=False,
        ),
        migrations.AlterUniqueTogether(
            name='dimension',
            unique_together=set([('agency', 'dim_id')]),
        ),
    ]
