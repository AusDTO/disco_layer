# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('govservices', '0012_auto_20150629_0850'),
    ]

    operations = [
        migrations.CreateModel(
            name='ServiceDimension',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('dim_id', models.CharField(max_length=512, null=True, blank=True)),
                ('name', models.CharField(max_length=512, null=True, blank=True)),
                ('dist', models.IntegerField(null=True, blank=True)),
                ('desc', models.TextField(null=True, blank=True)),
                ('infoUrl', models.CharField(max_length=512, null=True, blank=True)),
                ('agency', models.ForeignKey(to='govservices.Agency')),
            ],
        ),
    ]
