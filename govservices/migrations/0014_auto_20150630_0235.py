# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('govservices', '0013_servicedimension'),
    ]

    operations = [
        migrations.RenameField(
            model_name='servicedimension',
            old_name='infoUrl',
            new_name='info_url',
        ),
    ]
