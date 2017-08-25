# -*- coding: utf-8 -*-
# Generated by Django 1.11.2 on 2017-08-25 06:28
from __future__ import unicode_literals

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('scoreset', '0005_auto_20170825_1231'),
    ]

    operations = [
        migrations.AlterField(
            model_name='scoreset',
            name='created_by',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='last_created_scoreset', to=settings.AUTH_USER_MODEL, verbose_name='Created by'),
        ),
        migrations.AlterField(
            model_name='scoreset',
            name='last_edit_by',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='last_edited_scoreset', to=settings.AUTH_USER_MODEL, verbose_name='Last edited by'),
        ),
    ]
