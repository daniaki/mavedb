# -*- coding: utf-8 -*-
# Generated by Django 1.11.5 on 2018-06-18 06:43
from __future__ import unicode_literals

from django.db import migrations, models
import variant.validators


class Migration(migrations.Migration):

    dependencies = [
        ('variant', '0002_auto_20180510_1355'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='variant',
            name='hgvs',
        ),
        migrations.AddField(
            model_name='variant',
            name='hgvs_nt',
            field=models.TextField(default=None, null=True, validators=[variant.validators.validate_hgvs_string]),
        ),
        migrations.AddField(
            model_name='variant',
            name='hgvs_p',
            field=models.TextField(default=None, null=True, validators=[variant.validators.validate_hgvs_string]),
        ),
    ]