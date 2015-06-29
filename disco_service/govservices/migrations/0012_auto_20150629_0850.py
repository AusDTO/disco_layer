# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('govservices', '0011_agency'),
    ]

    operations = [
        migrations.AddField(
            model_name='service',
            name='agency',
            field=models.ForeignKey(default=1, to='govservices.Agency'),
        ),
        migrations.AddField(
            model_name='subservice',
            name='agency',
            field=models.ForeignKey(default=1, to='govservices.Agency'),
        ),
    ]
