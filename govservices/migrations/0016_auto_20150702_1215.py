# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('govservices', '0015_auto_20150701_0604'),
    ]

    operations = [
        migrations.CreateModel(
            name='Dimension',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('dim_id', models.CharField(max_length=512, null=True, blank=True)),
                ('name', models.CharField(max_length=512, null=True, blank=True)),
                ('dist', models.IntegerField(null=True, blank=True)),
                ('desc', models.TextField(null=True, blank=True)),
                ('info_url', models.CharField(max_length=512, null=True, blank=True)),
                ('agency', models.ForeignKey(to='govservices.Agency')),
            ],
        ),
        migrations.RemoveField(
            model_name='servicedimension',
            name='agency',
        ),
        migrations.AlterUniqueTogether(
            name='service',
            unique_together=set([('agency', 'src_id')]),
        ),
        migrations.AlterUniqueTogether(
            name='subservice',
            unique_together=set([('agency', 'cat_id')]),
        ),
        migrations.DeleteModel(
            name='ServiceDimension',
        ),
    ]
