# -*- coding: utf-8 -*-
# Generated by Django 1.11.5 on 2018-09-28 07:13
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0002_auto_20180510_1355'),
    ]

    operations = [
        migrations.AddField(
            model_name='profile',
            name='auth_token',
            field=models.CharField(default=None, max_length=64, null=True),
        ),
        migrations.AddField(
            model_name='profile',
            name='auth_token_expriy',
            field=models.DateField(default=None, null=True),
        ),
    ]