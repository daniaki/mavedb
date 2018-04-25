# -*- coding: utf-8 -*-
# Generated by Django 1.11.5 on 2018-04-25 04:28
from __future__ import unicode_literals

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dataset', '0003_auto_20180421_1521'),
    ]

    operations = [
        migrations.AlterField(
            model_name='experiment',
            name='creation_date',
            field=models.DateTimeField(default=datetime.datetime(2018, 4, 25, 14, 28, 19, 31529), verbose_name='Creation date'),
        ),
        migrations.AlterField(
            model_name='experiment',
            name='modification_date',
            field=models.DateTimeField(auto_now=True, verbose_name='Modification date'),
        ),
        migrations.AlterField(
            model_name='experimentset',
            name='creation_date',
            field=models.DateTimeField(default=datetime.datetime(2018, 4, 25, 14, 28, 19, 31529), verbose_name='Creation date'),
        ),
        migrations.AlterField(
            model_name='experimentset',
            name='modification_date',
            field=models.DateTimeField(auto_now=True, verbose_name='Modification date'),
        ),
        migrations.AlterField(
            model_name='scoreset',
            name='creation_date',
            field=models.DateTimeField(default=datetime.datetime(2018, 4, 25, 14, 28, 19, 31529), verbose_name='Creation date'),
        ),
        migrations.AlterField(
            model_name='scoreset',
            name='modification_date',
            field=models.DateTimeField(auto_now=True, verbose_name='Modification date'),
        ),
    ]