# -*- coding: utf-8 -*-
# Generated by Django 1.11.5 on 2018-07-18 09:16
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [("dataset", "0008_publicdatasetcounter")]

    operations = [
        migrations.RemoveField(
            model_name="publicdatasetcounter", name="experiments"
        ),
        migrations.RemoveField(
            model_name="publicdatasetcounter", name="scoresets"
        ),
    ]
