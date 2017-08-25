# -*- coding: utf-8 -*-
# Generated by Django 1.11.2 on 2017-08-25 02:31
from __future__ import unicode_literals

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('experiment', '0006_auto_20170824_1823'),
    ]

    operations = [
        migrations.AlterField(
            model_name='experiment',
            name='created_by',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='last_created_experiment', to=settings.AUTH_USER_MODEL, verbose_name='Created by'),
        ),
        migrations.AlterField(
            model_name='experiment',
            name='last_edit_by',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='last_edited_experiment', to=settings.AUTH_USER_MODEL, verbose_name='Last edited by'),
        ),
        migrations.AlterField(
            model_name='experimentset',
            name='created_by',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='last_created_experimentset', to=settings.AUTH_USER_MODEL, verbose_name='Created by'),
        ),
        migrations.AlterField(
            model_name='experimentset',
            name='last_edit_by',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='last_edited_experimentset', to=settings.AUTH_USER_MODEL, verbose_name='Last edited by'),
        ),
    ]
