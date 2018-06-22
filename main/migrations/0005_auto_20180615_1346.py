# -*- coding: utf-8 -*-
# Generated by Django 1.11.5 on 2018-06-15 03:46
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0004_auto_20180516_1100'),
    ]

    operations = [
        migrations.RenameField(
            model_name='siteinformation',
            old_name='about',
            new_name='md_about',
        ),
        migrations.RenameField(
            model_name='siteinformation',
            old_name='citation',
            new_name='md_citation',
        ),
        migrations.RenameField(
            model_name='siteinformation',
            old_name='documentation',
            new_name='md_documentation',
        ),
        migrations.RenameField(
            model_name='siteinformation',
            old_name='privacy',
            new_name='md_privacy',
        ),
        migrations.RenameField(
            model_name='siteinformation',
            old_name='terms',
            new_name='md_terms',
        ),
        migrations.RenameField(
            model_name='siteinformation',
            old_name='usage_guide',
            new_name='md_usage_guide',
        ),
    ]
