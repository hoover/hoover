# -*- coding: utf-8 -*-
# Generated by Django 1.10.3 on 2016-11-14 22:25
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('search', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='collection',
            name='loader_state',
            field=models.TextField(default='null'),
        ),
    ]
