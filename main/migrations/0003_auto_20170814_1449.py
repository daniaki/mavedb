# -*- coding: utf-8 -*-
# Generated by Django 1.11.2 on 2017-08-14 04:49
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0002_auto_20170812_1512'),
    ]

    operations = [
        migrations.AlterField(
            model_name='referencemapping',
            name='reference',
            field=models.CharField(default=None, max_length=256, verbose_name='Reference'),
        ),
    ]
