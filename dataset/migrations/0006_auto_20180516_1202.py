# -*- coding: utf-8 -*-
# Generated by Django 1.11.5 on 2018-05-16 02:02
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dataset', '0005_auto_20180510_1355'),
    ]

    operations = [
        migrations.AddField(
            model_name='experiment',
            name='last_urn_index',
            field=models.IntegerField(default=1),
        ),
        migrations.AddField(
            model_name='experimentset',
            name='last_urn_index',
            field=models.IntegerField(default=1),
        ),
        migrations.AddField(
            model_name='scoreset',
            name='last_urn_index',
            field=models.IntegerField(default=1),
        ),
    ]
