# -*- coding: utf-8 -*-
# Generated by Django 1.10.3 on 2016-11-24 03:52
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('teas', '0014_teassources_url'),
    ]

    operations = [
        migrations.DeleteModel(
            name='test',
        ),
    ]
