# -*- coding: utf-8 -*-
# Generated by Django 1.11.23 on 2020-09-16 21:17
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("dataset", "0014_scoreset_meta_analysis_for"),
    ]

    operations = [
        migrations.AlterField(
            model_name="scoreset",
            name="meta_analysis_for",
            field=models.ManyToManyField(
                blank=True,
                help_text="Select one or more score sets that this score set will create a meta-analysis for. Please leave the experiment field blank if this score set is a meta-analysis.",
                related_name="meta_analysed_by",
                to="dataset.ScoreSet",
                verbose_name="Meta-analysis for",
            ),
        ),
    ]
