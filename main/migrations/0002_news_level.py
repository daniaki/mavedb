# -*- coding: utf-8 -*-
# Generated by Django 1.11.5 on 2018-05-02 06:49
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='news',
            name='level',
            field=models.CharField(choices=[(0, 'April fools'), (1, 'Information'), (2, 'Important'), (3, 'Critical')], default=None, max_length=250),
        ),
    ]