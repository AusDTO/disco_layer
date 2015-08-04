# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('govservices', '0002_auto_20150627_0630'),
    ]

    operations = [
        migrations.CreateModel(
            name='LifeEvent',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('label', models.TextField()),
            ],
        ),
    ]
