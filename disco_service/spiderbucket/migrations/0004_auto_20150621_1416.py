# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('spiderbucket', '0003_auto_20150618_1343'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='page',
            name='document_decoded',
        ),
        migrations.RemoveField(
            model_name='page',
            name='excerpt',
        ),
        migrations.RemoveField(
            model_name='page',
            name='param_string',
        ),
        migrations.RemoveField(
            model_name='page',
            name='title',
        ),
    ]
