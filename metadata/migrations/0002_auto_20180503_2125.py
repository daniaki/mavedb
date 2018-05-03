# -*- coding: utf-8 -*-
# Generated by Django 1.11.5 on 2018-05-03 11:25
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion
import metadata.validators


class Migration(migrations.Migration):

    dependencies = [
        ('genome', '0003_auto_20180501_1420'),
        ('metadata', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='ensembloffset',
            name='identifier',
            field=models.ForeignKey(default=None, on_delete=django.db.models.deletion.CASCADE, related_name='offset', to='metadata.EnsemblIdentifier', validators=[metadata.validators.validate_ensembl_identifier], verbose_name='Ensembl accession'),
        ),
        migrations.AlterField(
            model_name='ensembloffset',
            name='target',
            field=models.ForeignKey(default=None, on_delete=django.db.models.deletion.CASCADE, related_name='ensembloffset', to='genome.TargetGene', verbose_name='Target gene'),
        ),
        migrations.AlterField(
            model_name='refseqoffset',
            name='identifier',
            field=models.ForeignKey(default=None, on_delete=django.db.models.deletion.CASCADE, related_name='offset', to='metadata.RefseqIdentifier', validators=[metadata.validators.validate_refseq_identifier], verbose_name='RefSeq accession'),
        ),
        migrations.AlterField(
            model_name='refseqoffset',
            name='target',
            field=models.ForeignKey(default=None, on_delete=django.db.models.deletion.CASCADE, related_name='refseqoffset', to='genome.TargetGene', verbose_name='Target gene'),
        ),
        migrations.AlterField(
            model_name='uniprotoffset',
            name='identifier',
            field=models.ForeignKey(default=None, on_delete=django.db.models.deletion.CASCADE, related_name='offset', to='metadata.UniprotIdentifier', validators=[metadata.validators.validate_uniprot_identifier], verbose_name='UniProt accession'),
        ),
        migrations.AlterField(
            model_name='uniprotoffset',
            name='target',
            field=models.ForeignKey(default=None, on_delete=django.db.models.deletion.CASCADE, related_name='uniprotoffset', to='genome.TargetGene', verbose_name='Target gene'),
        ),
        migrations.AlterUniqueTogether(
            name='ensembloffset',
            unique_together=set([('target', 'identifier')]),
        ),
        migrations.AlterUniqueTogether(
            name='refseqoffset',
            unique_together=set([('target', 'identifier')]),
        ),
        migrations.AlterUniqueTogether(
            name='uniprotoffset',
            unique_together=set([('target', 'identifier')]),
        ),
    ]