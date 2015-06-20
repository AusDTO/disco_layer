# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Page',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('protocol', models.CharField(max_length=6)),
                ('domain', models.CharField(max_length=256)),
                ('url', models.CharField(max_length=256, null=True, blank=True)),
                ('param_string', models.TextField(null=True, blank=True)),
                ('title', models.TextField(null=True, blank=True)),
                ('excerpt', models.TextField()),
            ],
        ),
    ]
