# -*- coding: utf-8 -*-
# Generated by Django 1.10.3 on 2016-11-24 03:40
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('teas', '0006_teassources'),
    ]

    operations = [
        migrations.CreateModel(
            name='text',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
            ],
        ),
    ]
