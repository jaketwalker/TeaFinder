# -*- coding: utf-8 -*-
# Generated by Django 1.10.3 on 2016-11-24 03:45
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('teas', '0011_test'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='test',
            name='ProductID',
        ),
    ]
