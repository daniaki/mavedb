import os
import sys
import json

from django.conf import settings

from genome.models import ReferenceGenome
from metadata.models import GenomeIdentifier

from django.core.management.base import BaseCommand


class Command(BaseCommand):
    def handle(self, *args, **kwargs):
        path = os.path.join(settings.GENOME_DIR, 'reference_genomes.json')
        with open(path, 'rt') as fp:
            references = json.load(fp)
            for reference_attrs in references:
                name = reference_attrs['short_name']
                species = reference_attrs['species_name']
                assembly = reference_attrs['assembly_identifier']
                if assembly is not None:
                    identifier = assembly['identifier']
                else:
                    identifier = None

                if not ReferenceGenome.objects.filter(short_name=name).count():
                    genome_id = None
                    if identifier:
                        genome_id, _ = GenomeIdentifier.objects.get_or_create(
                            identifier=identifier)
                    params = {
                        'short_name': name,
                        'species_name': species,
                        'genome_id': genome_id
                    }
                    sys.stdout.write("Create reference '%s'\n" % name)
                    ReferenceGenome.objects.create(**params)
                else:
                    sys.stdout.write("Reference '%s' already exists\n" % name)
