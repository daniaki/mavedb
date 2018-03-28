from io import TextIOWrapper

import django.forms as forms
from django.db import transaction
from django.core.exceptions import ValidationError
from django.utils.translation import ugettext

from main.models import Licence

from metadata.validators import (
    validate_keyword_list, validate_pubmed_list,
    validate_sra_list, validate_doi_list
)
from metadata.fields import ModelSelectMultipleField
from metadata.models import (
    Keyword, SraIdentifier,
    DoiIdentifier, PubmedIdentifier
)

from genome.models import TargetOrganism
from genome.validators import (
    validate_target_organism,
    validate_wildtype_sequence, 
    validate_target_gene
)

import dataset.constants as constants

from .models import DatasetModel
from .models import Experiment, ScoreSet, ExperimentSet
from variant.models import Variant

from .validators import (
    validate_scoreset_count_data_input, validate_scoreset_score_data_input,
    validate_scoreset_json, validate_csv_extension
)
from variant.validators import validate_variant_rows


class DatasetModelForm(forms.ModelForm):
    """
    Base form handling the fields present in :class:`.models.DatasetModel`

    Parameters
    ----------
    user : :class:`User`
        The user instance that this form is served to.
    """
    M2M_FIELD_NAMES = (
        'keywords',
        'sra_ids',
        'doi_ids',
        'pmid_ids'
    )

    class Meta:
        model = DatasetModel
        fields = (
            'abstract_text',
            'method_text',
            'keywords',
            'sra_ids',
            'doi_ids',
            'pmid_ids'
        )

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user')
        super().__init__(*args, **kwargs)

        self.fields['abstract_text'].widget = forms.Textarea(
            attrs={"class": "form-control"}
        )
        self.fields['method_text'].widget = forms.Textarea(
            attrs={"class": "form-control"}
        )
        self.fields['keywords'] = ModelSelectMultipleField(
            klass=Keyword, to_field_name='text',
            label='Keywords', required=False,
            queryset=Keyword.objects.all(), widget=forms.SelectMultiple(
                attrs={"class": "form-control select2 select2-token-select"}
            )
        )
        self.fields['sra_ids'] = ModelSelectMultipleField(
            klass=SraIdentifier, to_field_name='identifier',
            label='SRA Identifiers', required=False,
            queryset=SraIdentifier.objects.all(), widget=forms.SelectMultiple(
                attrs={"class": "form-control select2 select2-token-select"}
            )
        )
        self.fields['doi_ids'] = ModelSelectMultipleField(
            klass=DoiIdentifier, to_field_name='identifier',
            label='DOI Identifiers', required=False,
            queryset=DoiIdentifier.objects.all(), widget=forms.SelectMultiple(
                attrs={"class": "form-control select2 select2-token-select"}
            )
        )
        self.fields['pmid_ids'] = ModelSelectMultipleField(
            klass=PubmedIdentifier, to_field_name='identifier',
            label='PubMed Identifiers', required=False,
            queryset=PubmedIdentifier.objects.all(), widget=forms.SelectMultiple(
                attrs={"class": "form-control select2 select2-token-select"}
            )
        )
        self.fields['keywords'].validators.append(validate_keyword_list)
        self.fields['sra_ids'].validators.append(validate_sra_list)
        self.fields['doi_ids'].validators.append(validate_doi_list)
        self.fields['pmid_ids'].validators.append(validate_pubmed_list)

    def _clean_field_name(self, field_name):
        field = self.fields[field_name]
        cleaned_queryset = self.cleaned_data[field_name]
        all_instances = list(cleaned_queryset.all()) + field.create_new()
        return all_instances

    def clean_keywords(self):
        return self._clean_field_name('keywords')

    def clean_sra_ids(self):
        return self._clean_field_name('sra_ids')

    def clean_doi_ids(self):
        return self._clean_field_name('doi_ids')

    def clean_pmid_ids(self):
        return self._clean_field_name('pmid_ids')

    def _save_m2m(self):
        # Save all instances before calling super() so that all new instances
        # are in the database before m2m relationships are created.
        for m2m_field in self.M2M_FIELD_NAMES:
            if m2m_field in self.fields:
                for instance in self.cleaned_data.get(m2m_field, []):
                    instance.save()
                self.instance.clear_m2m(m2m_field)
        super()._save_m2m()  # super() will create new m2m relationships

    # Make this atomic since new m2m instances will need to be saved.
    @transaction.atomic
    def save(self, commit=True):
        super().save(commit=commit)
        if commit:
            self.instance.set_last_edit_by(self.user)
            if not hasattr(self, 'edit_mode'):
                self.instance.set_created_by(self.user)
            self.instance.save()
        return self.instance

    def m2m_instances_for_field(self, field_name, return_new=True):
        if field_name not in self.fields:
            raise ValueError(
                '{} is not a field in this form.'.format(field_name)
            )
        existing_entries = [i for i in self.cleaned_data.get(field_name, [])]
        if return_new:
            new_entries = self.fields[field_name].new_instances
            return existing_entries + new_entries
        return existing_entries

    @classmethod
    def from_request(cls, request, instance):
        if request.method == "POST":
            form = cls(
                user=request.user, data=request.POST,
                files=request.FILES, instance=instance)
        else:
            form = cls(user=request.user, instance=instance)
        return form


class ExperimentForm(DatasetModelForm):
    """
    Docstring
    """
    class Meta(DatasetModel.Meta):
        model = Experiment
        fields = DatasetModelForm.Meta.fields + (
            'experimentset',
            'target',
            'wt_sequence',
            'target_organism',
        )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields['experimentset'] = forms.ModelChoiceField(
            queryset=None, required=False, widget=forms.Select(
                attrs={"class": "form-control"})
        )
        self.fields['target_organism'] = ModelSelectMultipleField(
            klass=TargetOrganism, to_field_name='text',
            required=False, queryset=None, widget=forms.SelectMultiple(
                attrs={"class": "form-control select2 select2-token-select"})
        )
        self.fields['wt_sequence'].widget = forms.Textarea(
            attrs={"class": "form-control"})

        # TODO: This will become a Foreign Key field when
        # Target becomes a table
        self.fields['target'].widget = forms.TextInput(
            attrs={"class": "form-control"})

        self.fields["target"].validators.append(validate_target_gene)
        self.fields["target_organism"].validators.append(
            validate_target_organism)
        self.fields["wt_sequence"].validators.append(
            validate_wildtype_sequence)

        self.fields["target_organism"].queryset = TargetOrganism.objects.all()
        # Populate the experimentset drop down with a list of experimentsets
        # that the user for this form has write access to.
        self.set_experimentset_options()

    def clean_target_organism(self):
        return self._clean_field_name('target_organism')

    def _save_m2m(self):
        # Save all target_organism instances before calling super()
        # so that all new instances are in the database before m2m
        # relationships are created.
        if 'target_organism' in self.fields:
            for instance in self.cleaned_data.get('target_organism'):
                instance.save()
            self.instance.clear_m2m('target_organism')
        super()._save_m2m()

    @transaction.atomic
    def save(self, commit=True):
        super().save(commit=commit)

    def set_experimentset_options(self):
        if 'experimentset' in self.fields:
            choices = self.user.profile.administrator_experimentsets() + \
                      self.user.profile.contributor_experimentsets()
            choices_qs = ExperimentSet.objects.filter(
                pk__in=set([i.pk for i in choices])).order_by("urn")
            self.fields["experimentset"].queryset = choices_qs

    @classmethod
    def from_request(cls, request, instance):
        form = super().from_request(request, instance)
        form.set_experimentset_options()
        return form


class ExperimentEditForm(ExperimentForm):
    """
    A subset of `ExperimentForm` for editiing instances. Follows the same
    logic as `ExperimentForm`
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.edit_mode = True
        self.fields.pop('target_organism')
        self.fields.pop('target')
        self.fields.pop('wt_sequence')
        self.fields.pop('experimentset')


# --------------------------------------------------------------------------- #
#                           ScoreSet Form
# --------------------------------------------------------------------------- #
class ScoreSetForm(DatasetModelForm):
    """
    This form is presented on the create new scoreset view. It contains
    all the validation logic required to ensure that a score dataset and
    counts dataset are parsed into valid Variant objects that are associated
    with the created scoreset. It also defines additional validation for
    the `replaces` field in scoreset to make sure that the selected
    `ScoreSet` is a member of the selected `Experiment` instance.
    """
    class Meta(DatasetModelForm.Meta):
        model = ScoreSet
        fields = DatasetModelForm.Meta.fields + (
            'experiment',
            'licence',
            'replaces'
        )

    score_data = forms.FileField(
        required=True, label="Variant score data (required)",
        validators=[validate_scoreset_score_data_input, validate_csv_extension],
        widget=forms.widgets.FileInput(attrs={"accept": "csv"})
    )
    count_data = forms.FileField(
        required=False, label="Variant count data (optional)",
        validators=[validate_scoreset_count_data_input, validate_csv_extension],
        widget=forms.widgets.FileInput(attrs={"accept": "csv"})
    )

    def __init__(self, *args, **kwargs):
        super(ScoreSetForm, self).__init__(*args, **kwargs)

        # This will be used later after score/count files have been read in
        # to store the headers.
        self.dataset_columns = {
            constants.score_columns: [],
            constants.count_columns: [],
            constants.metadata_columns: []
        }

        self.fields['experiment'] = forms.ModelChoiceField(
            queryset=None, required=True, widget=forms.Select(
                attrs={"class": "form-control"}))
        self.fields['replaces'] = forms.ModelChoiceField(
            queryset=None, required=False, widget=forms.Select(
                attrs={"class": "form-control"}))
        self.fields['licence'] = forms.ModelChoiceField(
            queryset=Licence.objects.all(), required=False,
            widget=forms.Select(
                attrs={"class": "form-control"}))

        self.fields["replaces"].required = False
        self.set_replaces_options()

        self.set_experiment_options()
        self.fields['experiment'].empty_label = 'Create new experiment'

        self.fields["licence"].required = False
        if not self.fields["licence"].initial:
            self.fields["licence"].initial = Licence.get_default()
        self.fields["licence"].empty_label = 'Default'

    def clean_licence(self):
        licence = self.cleaned_data.get("licence", None)
        if not licence:
            licence = Licence.objects.get(short_name="CC BY-NC-SA 4.0")
        return licence

    def clean_replaces(self):
        scoreset = self.cleaned_data.get("replaces", None)
        experiment = self.cleaned_data.get("experiment", None)
        if scoreset is not None and experiment is not None:
            if scoreset not in experiment.scoresets.all():
                raise ValidationError(
                    ugettext(
                        "Replaces field selection must be a member of the "
                        "selected experiment."
                    ))
        return scoreset

    def clean_score_data(self):
        score_file = self.cleaned_data.get("score_data", None)
        if not score_file:
            return {}
        # Don't need to wrap this in a try/catch as the form
        # will catch any Validation errors automagically.
        #   Valdator must check the following:
        #       Header has hgvs and at least one other column
        #       Number of rows does not match header
        #       Datatypes of rows match
        #       HGVS string is a valid hgvs string
        #       Hgvs appears more than once in rows
        score_file = TextIOWrapper(score_file, encoding='utf-8')
        header, hgvs_score_map = validate_variant_rows(score_file)
        self.dataset_columns[constants.score_columns] = header
        return hgvs_score_map

    def clean_count_data(self):
        count_file = self.cleaned_data.get("count_data", None)
        if not count_file:
            return {}
        # Don't need to wrap this in a try/catch as the form
        # will catch any Validation errors automagically.
        #   Valdator must check the following:
        #       Header has hgvs and at least one other column
        #       Number of rows does not match header
        #       Datatypes of rows match
        #       HGVS string is a valid hgvs string
        #       Hgvs appears more than once in rows
        count_file = TextIOWrapper(count_file, encoding='utf-8')
        header, hgvs_count_map = validate_variant_rows(count_file)
        self.dataset_columns[constants.count_columns] = header
        return hgvs_count_map

    @staticmethod
    def _fill_in_missing(hgvs_keys, mapping):
        # This function has side-effects - it creates new keys in the default
        # dict `mapping`.
        for key in hgvs_keys:
            _ = mapping[key]
            mapping[key][constants.hgvs_column] = key
        return mapping

    def clean(self):
        if self.errors:
            # There are errors, maybe from the `clean_<field_name>` methods.
            # End here and run the parent method to quickly return the form.
            return super().clean()

        cleaned_data = super().clean()
        score_data_field = self.fields.get("score_data", None)
        scores_required = False if not score_data_field else \
            score_data_field.required

        hgvs_score_map = cleaned_data.get("score_data", {})
        hgvs_count_map = cleaned_data.get("count_data", {})
        hgvs_meta_map = cleaned_data.get("meta_data", {})

        has_score_data = len(hgvs_score_map) > 0
        has_count_data = len(hgvs_count_map) > 0
        has_meta_data = len(hgvs_meta_map) > 0

        # In edit mode, we have relaxed the requirement of uploading a score
        # dataset since one already exists.
        if scores_required and not has_score_data and \
                not hasattr(self, "edit_mode"):
            raise ValidationError(
                ugettext(
                    "Score data cannot be empty and must contain at "
                    "least one row with non-null values"
                )
            )
        # In edit, mode if a user tries to submit a new count dataset without
        # an accompanying score dataset, this error will be thrown. We could
        # relax this but there is the potential that the user might upload
        # a new count dataset and forget to upload a new score dataset.
        if (has_count_data or has_meta_data) and not has_score_data:
            raise ValidationError(
                ugettext(
                    "You must upload an accompanying score data file when "
                    "uploading a new count/meta data file, or replacing an "
                    "existing one."
                )
            )

        # TODO: Handle the cases where count/meta data is not posted
        if has_count_data:
            # For every hgvs in scores but not in counts, fill in the
            # counts columns (if a counts dataset is supplied) with null values
            self._fill_in_missing(hgvs_score_map.keys(), hgvs_count_map)
            # For every hgvs in counts but not in scores, fill in the
            # scores columns with null values.
            self._fill_in_missing(hgvs_count_map.keys(), hgvs_score_map)

        # Re-build the variants if any new files have been processed.
        # If has_count_data is true then has_score_data should also be true.
        # The reverse is not always true.
        if has_score_data:
            validate_scoreset_json(self.dataset_columns)
            variants = dict()

            for hgvs in hgvs_score_map.keys():
                scores_json = hgvs_score_map[hgvs]
                counts_json = hgvs_count_map[hgvs] if has_count_data else {}
                data = {
                    constants.variant_score_data: scores_json,
                    constants.variant_count_data: counts_json,
                    constants.variant_metadata: {}
                }
                variant = Variant(scoreset=self.instance, hgvs=hgvs, data=data)
                variants[hgvs] = variant

            cleaned_data["variants"] = variants

        return cleaned_data

    def _save_m2m(self):
        variants = self.get_variants()
        if variants:  # No variants if in edit mode and no new files uploaded.
            self.instance.delete_variants()
            for _, variant in variants.items():
                variant.save()
                self.instance.variants.add(variant)
        super()._save_m2m()

    @transaction.atomic
    def save(self, commit=True):
        return super().save(commit=commit)

    def get_variants(self):
        return self.cleaned_data.get('variants', {})

    def set_replaces_options(self):
        if 'replaces' in self.fields:
            choices = self.user.profile.administrator_scoresets() + \
                self.user.profile.contributor_scoresets()
            scoresets_qs = ScoreSet.objects.filter(
                pk__in=set([i.pk for i in choices])).order_by("urn")
            self.fields["replaces"].queryset = scoresets_qs

    def set_experiment_options(self):
        if 'experiment' in self.fields:
            choices = self.user.profile.administrator_experiments() + \
                self.user.profile.contributor_experiments()
            experiment_qs = Experiment.objects.filter(
                pk__in=set([i.pk for i in choices])).order_by("urn")
            self.fields["experiment"].queryset = experiment_qs

    @classmethod
    def from_request(cls, request, instance):
        form = super().from_request(request, instance)
        form.set_replaces_options()
        form.set_experiment_options()
        return form


class ScoreSetEditForm(ScoreSetForm):
    """
    Subset of the `ScoreSetForm`, which freezes all fields except `private`,
    `doi_id`, `keywords`, `abstract` and `method_desc`. Only these fields
    are editable.
    """
    class Meta(ScoreSetForm.Meta):
        model = ScoreSet

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.edit_mode = True
        self.fields.pop('experiment')
        self.fields.pop('score_data')
        self.fields.pop('count_data')
        self.fields.pop('licence')
        self.fields.pop('replaces')
