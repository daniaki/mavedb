# -*- coding: utf-8 -*-
# Generated by Django 1.11.2 on 2017-08-16 09:18
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('scoreset', '0002_auto_20170815_1423'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='scoreset',
            options={'ordering': ['-creation_date'], 'permissions': (('can_view', 'Can view'), ('can_edit', 'Can edit'), ('can_manage', 'Can manage')), 'verbose_name': 'ScoreSet', 'verbose_name_plural': 'ScoreSets'},
        ),
    ]
