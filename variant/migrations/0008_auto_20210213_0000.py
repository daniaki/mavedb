# -*- coding: utf-8 -*-
# Generated by Django 1.11.23 on 2021-02-12 13:00
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("variant", "0007_auto_20200907_1158"),
    ]

    operations = [
        migrations.RenameField(
            model_name="variant",
            old_name="hgvs_tx",
            new_name="hgvs_splice",
        ),
    ]
