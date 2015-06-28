# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('govservices', '0008_auto_20150628_1152'),
    ]

    operations = [
        migrations.RenameField(
            model_name='service',
            old_name='aervice_tags',
            new_name='service_tags',
        ),
    ]
