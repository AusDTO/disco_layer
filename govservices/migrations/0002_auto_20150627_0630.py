# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('govservices', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='ServiceTag',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('label', models.CharField(max_length=512)),
            ],
        ),
        migrations.AlterField(
            model_name='subservice',
            name='desc',
            field=models.TextField(null=True, blank=True),
        ),
        migrations.AlterField(
            model_name='subservice',
            name='name',
            field=models.CharField(max_length=512, null=True, blank=True),
        ),
    ]
