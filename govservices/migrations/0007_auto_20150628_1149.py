# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('govservices', '0006_auto_20150628_1141'),
    ]

    operations = [
        migrations.RenameField(
            model_name='service',
            old_name='incedental',
            new_name='incidental',
        ),
    ]
