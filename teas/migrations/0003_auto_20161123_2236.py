# -*- coding: utf-8 -*-
# Generated by Django 1.10.3 on 2016-11-24 03:36
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('teas', '0002_auto_20161123_2235'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='teassources',
            name='SourceID',
        ),
        migrations.RemoveField(
            model_name='teassources',
            name='TeaID',
        ),
        migrations.DeleteModel(
            name='TeasSources',
        ),
    ]
