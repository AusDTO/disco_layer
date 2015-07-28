# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('spiderbucket', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='page',
            name='domain',
        ),
        migrations.AddField(
            model_name='page',
            name='depth',
            field=models.IntegerField(max_length=256, null=True, blank=True),
        ),
        migrations.AddField(
            model_name='page',
            name='document',
            field=models.TextField(null=True, blank=True),
        ),
        migrations.AddField(
            model_name='page',
            name='document_decoded',
            field=models.TextField(null=True, blank=True),
        ),
        migrations.AddField(
            model_name='page',
            name='fetched',
            field=models.NullBooleanField(),
        ),
        migrations.AddField(
            model_name='page',
            name='host',
            field=models.CharField(max_length=256, null=True, blank=True),
        ),
        migrations.AddField(
            model_name='page',
            name='lastFetchDateTime',
            field=models.DateTimeField(null=True, blank=True),
        ),
        migrations.AddField(
            model_name='page',
            name='nextFetchDateTime',
            field=models.DateTimeField(null=True, blank=True),
        ),
        migrations.AddField(
            model_name='page',
            name='orient_class',
            field=models.CharField(default='webDocumentContainer', max_length=256),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='page',
            name='orient_rid',
            field=models.CharField(default='delme', max_length=256),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='page',
            name='orient_version',
            field=models.CharField(default='delme', max_length=256),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='page',
            name='path',
            field=models.TextField(null=True, blank=True),
        ),
        migrations.AddField(
            model_name='page',
            name='port',
            field=models.IntegerField(max_length=256, null=True, blank=True),
        ),
        migrations.AddField(
            model_name='page',
            name='status',
            field=models.CharField(max_length=256, null=True, blank=True),
        ),
        migrations.AlterField(
            model_name='page',
            name='excerpt',
            field=models.TextField(null=True, blank=True),
        ),
        migrations.AlterField(
            model_name='page',
            name='protocol',
            field=models.CharField(max_length=6, null=True, blank=True),
        ),
        migrations.AlterField(
            model_name='page',
            name='url',
            field=models.CharField(default='delme', max_length=256),
            preserve_default=False,
        ),
    ]
