# -*- coding: utf-8 -*-
# Generated by Django 1.11.2 on 2017-08-07 03:27
from __future__ import unicode_literals

import datetime
import django.contrib.postgres.fields.jsonb
import django.core.validators
from django.db import migrations, models
import django.db.models.deletion
import scoreset.validators


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('experiment', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='ScoreSet',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('accession', models.CharField(default=None, max_length=64, null=True, unique=True, validators=[scoreset.validators.valid_scs_accession], verbose_name='Accession')),
                ('creation_date', models.DateField(default=datetime.date.today, verbose_name='Creation date')),
                ('approved', models.BooleanField(default=False, verbose_name='Approved')),
                ('last_used_suffix', models.IntegerField(default=0, validators=[django.core.validators.MinValueValidator(limit_value=0)])),
                ('private', models.BooleanField(default=True, verbose_name='Private')),
                ('abstract', models.TextField(blank=True, default='', verbose_name='Abstract')),
                ('method_desc', models.TextField(blank=True, default='', verbose_name='Method description')),
                ('doi_id', models.TextField(blank=True, default='', verbose_name='DOI identifier')),
                ('dataset_columns', django.contrib.postgres.fields.jsonb.JSONField(default={'counts': ['count'], 'scores': ['score', 'SE']}, validators=[scoreset.validators.valid_scoreset_json], verbose_name='Dataset columns')),
                ('experiment', models.ForeignKey(default=None, on_delete=django.db.models.deletion.PROTECT, to='experiment.Experiment')),
            ],
            options={
                'verbose_name': 'ScoreSet',
                'verbose_name_plural': 'ScoreSets',
                'ordering': ['-creation_date'],
            },
        ),
        migrations.CreateModel(
            name='Variant',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('accession', models.CharField(default=None, max_length=64, null=True, unique=True, validators=[scoreset.validators.valid_var_accession], verbose_name='Accession')),
                ('creation_date', models.DateField(default=datetime.date.today, verbose_name='Creation date')),
                ('hgvs_string', models.TextField(default=None, validators=[scoreset.validators.valid_hgvs_string])),
                ('data', django.contrib.postgres.fields.jsonb.JSONField(default={'counts': {'count': [None]}, 'scores': {'SE': [None], 'score': [None]}}, validators=[scoreset.validators.valid_variant_json], verbose_name='Data columns')),
                ('scoreset', models.ForeignKey(default=None, on_delete=django.db.models.deletion.PROTECT, to='scoreset.ScoreSet')),
            ],
            options={
                'verbose_name': 'Variant',
                'verbose_name_plural': 'Variants',
                'ordering': ['-creation_date'],
            },
        ),
    ]
