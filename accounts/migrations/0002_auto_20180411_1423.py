# -*- coding: utf-8 -*-
# Generated by Django 1.11.5 on 2018-04-11 04:23
from __future__ import unicode_literals

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0001_initial'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='profile',
            options={'ordering': ['-creation_date']},
        ),
        migrations.AddField(
            model_name='profile',
            name='creation_date',
            field=models.DateField(default=datetime.date.today, verbose_name='Creation date'),
        ),
        migrations.AddField(
            model_name='profile',
            name='modification_date',
            field=models.DateField(default=datetime.date.today, verbose_name='Modification date'),
        ),
    ]