# -*- coding: utf-8 -*-
# Generated by Django 1.9.3 on 2016-03-08 06:54
from __future__ import unicode_literals

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('appy', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='position',
            name='created_at',
            field=models.DateTimeField(auto_now_add=True, default=datetime.datetime(2016, 3, 7, 22, 54, 17, 672746)),
            preserve_default=False,
        ),
    ]