# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('govservices', '0004_servicetype'),
    ]

    operations = [
        migrations.CreateModel(
            name='Service',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('old_src_id', models.IntegerField(null=True, blank=True)),
                ('src_id', models.IntegerField(null=True, blank=True)),
                ('info_url', models.CharField(max_length=512, null=True, blank=True)),
                ('name', models.CharField(max_length=512, null=True, blank=True)),
                ('acronym', models.CharField(max_length=512, null=True, blank=True)),
                ('tagline', models.CharField(max_length=512, null=True, blank=True)),
                ('primaryAudience', models.CharField(max_length=512, null=True, blank=True)),
                ('analyticsAvailable', models.CharField(max_length=512, null=True, blank=True)),
                ('incedental', models.CharField(max_length=512, null=True, blank=True)),
                ('secondary', models.CharField(max_length=512, null=True, blank=True)),
                ('src_type', models.CharField(max_length=512, null=True, blank=True)),
                ('description', models.TextField(null=True, blank=True)),
                ('comment', models.TextField(null=True, blank=True)),
                ('current', models.CharField(max_length=512, null=True, blank=True)),
                ('aervice_tags', models.ManyToManyField(to='govservices.ServiceTag')),
                ('life_events', models.ManyToManyField(to='govservices.LifeEvent')),
                ('service_types', models.ManyToManyField(to='govservices.ServiceType')),
            ],
        ),
    ]
