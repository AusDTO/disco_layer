# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('govservices', '0007_auto_20150628_1149'),
    ]

    operations = [
        migrations.RenameField(
            model_name='service',
            old_name='analyticsAvailable',
            new_name='analytics_available',
        ),
        migrations.RenameField(
            model_name='service',
            old_name='primaryAudience',
            new_name='primary_audience',
        ),
    ]
