# -*- coding: utf-8 -*-
# Generated by Django 1.11.5 on 2018-05-09 04:00
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('genome', '0002_auto_20180504_1101'),
    ]

    operations = [
        migrations.AlterField(
            model_name='targetgene',
            name='wt_sequence',
            field=models.OneToOneField(default=None, on_delete=django.db.models.deletion.PROTECT, related_name='target', to='genome.WildTypeSequence', verbose_name='Wild-type Sequence'),
        ),
    ]