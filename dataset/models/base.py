import datetime

from django.contrib.auth import get_user_model
from django.contrib.postgres.fields import JSONField
from django.core.validators import MinValueValidator
from django.db import models, transaction

from accounts.mixins import GroupPermissionMixin
from main.utils import pandoc as pandoc
from metadata.models import (
    Keyword, SraIdentifier, DoiIdentifier,
    PubmedIdentifier, ExternalIdentifier
)
from urn.models import UrnModel


User = get_user_model()


class DatasetModel(UrnModel, GroupPermissionMixin):
    """
    This is the abstract base class for ExperimentSet, Experiment, and
    ScoreSet classes. It includes permissions, creation/edit details, shared
    metadata, and behaviors for displaying and formatting the metadata.

    Parameters
    ----------
    creation_date : `models.DataField`
        Data of instantiation in yyyy-mm-dd format.

    last_edit_date : `models.DataField`
        Data of instantiation in yyyy-mm-dd format. Updates everytime `save`
        is called.

    publish_date : `models.DataField`
        Data of instantiation in yyyy-mm-dd format. Updates when `publish` is
        called.

    created_by : `models.ForeignKey`
        User the instance was created by.

    last_edit_by : `models.ForeignKey`
        User to make the latest change to the instance.

    approved : `models.BooleanField`
        The approved status, as seen by the database admin. Instances are
        created by default as not approved and must be manually checked
        before going live.

    private : `models.BooleanField`
        Whether this experiment should be private and viewable only by
        those approved in the permissions.

    last_child_value : `models.IntegerField`
        Min value of 0. Counts how many child entities have been associated
        with this entity. Must be incremented on child creation. Used to
        generate urn numbers for new child entries.

    extra_metadata : `models.JSONField`
        Free-form json metadata that might be associated with this entry.

    abstract_text : `models.TextField`
        A markdown text blob for the abstract.

    method_text : `models.TextField`
        A markdown text blob for the methods description.

    keywords : `models.ManyToManyField`
        Associated `Keyword` objects for this entry.

    sra_ids : `models.ManyToManyField`
        Associated `ExternalIdentifier` objects for this entry that map to the
        NCBI Sequence Read Archive (https://www.ncbi.nlm.nih.gov/sra).

    doi_ids : `models.ManyToManyField`
        Associated `ExternalIdentifier` objects for this entry that map to
        Digital Object Identifiers (https://www.doi.org). These are intended to
        be used for data objects rather than publications.

    pmid_ids : `models.ManyToManyField`
        Associated `ExternalIdentifier` objects for this entry that map to
        NCBI PubMed identifiers (https://www.ncbi.nlm.nih.gov/pubmed). These
        will be formatted and displayed as publications.
    """
    class Meta:
        abstract = True
        ordering = ['-creation_date']

    # ---------------------------------------------------------------------- #
    #                       Model fields
    # ---------------------------------------------------------------------- #
    creation_date = models.DateField(
        blank=False,
        null=False,
        default=datetime.date.today,
        verbose_name="Created on",
    )

    last_edit_date = models.DateField(
        blank=False,
        null=False,
        default=datetime.date.today,
        verbose_name="Last edited on",
    )

    publish_date = models.DateField(
        blank=False,
        null=True,
        default=None,
        verbose_name="Published on",
    )

    last_edit_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        verbose_name="Last edited by",
        related_name='last_edited_%(class)s',
    )

    created_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        verbose_name="Created by",
        related_name='last_created_%(class)s',
    )

    approved = models.BooleanField(
        blank=False,
        null=False,
        default=False,
        verbose_name="Approved",
    )

    private = models.BooleanField(
        blank=False,
        null=False,
        default=True,
        verbose_name="Private",
    )

    last_child_value = models.IntegerField(
        default=0,
        validators=[MinValueValidator(limit_value=0)],
    )

    extra_metadata = JSONField(
        blank=True,
        default={},
        verbose_name="Additional metadata",
    )

    abstract_text = models.TextField(
        blank=True,
        default="",
        verbose_name="Abstract",
    )
    method_text = models.TextField(
        blank=True,
        default="",
        verbose_name="Method description"
    )

    # ---------------------------------------------------------------------- #
    #                       Optional Model fields
    # ---------------------------------------------------------------------- #
    keywords = models.ManyToManyField(
        Keyword, blank=True, verbose_name='Keywords')
    sra_ids = models.ManyToManyField(
        SraIdentifier, blank=True, verbose_name='SRA Identifiers')
    doi_ids = models.ManyToManyField(
        DoiIdentifier, blank=True, verbose_name='DOI Identifiers')
    pmid_ids = models.ManyToManyField(
        PubmedIdentifier, blank=True, verbose_name='PubMed Identifiers')

    # ---------------------------------------------------------------------- #
    #                       Methods
    # ---------------------------------------------------------------------- #
    def propagate_set_value(self, attr, value):
        """
        Private method for setting fields that also need to propagate upwards.
        For example, setting publishing a scoreset should also set the private
        bits on the parent experiment and experimentset.

        Parameters
        ----------
        attr : str
            Field name to set attribute of.
        value : any
            Value to set.
        """
        if hasattr(self, attr):
            self.__setattr__(attr, value)
        if hasattr(self, 'experiment'):
            self.experiment.propagate_set_value(attr, value)
        if hasattr(self, 'experimentset'):
            self.experimentset.propagate_set_value(attr, value)

    @transaction.atomic
    def save(self, save_parents=False, *args, **kwargs):
        self.last_edit_date = datetime.date.today()
        super().save(*args, **kwargs)
        if save_parents:
            self.save_parents(*args, **kwargs)

    def save_parents(self, *args, **kwargs):
        if hasattr(self, 'experiment'):
            self.experiment.save(*args, **kwargs)
            self.experiment.save_parents(*args, **kwargs)
        if hasattr(self, 'experimentset'):
            self.experimentset.save(*args, **kwargs)

    def publish(self, propagate=True):
        if propagate:
            self.propagate_set_value('private', False)
            self.propagate_set_value('publish_date', datetime.date.today())
        else:
            self.private = False
            self.publish_date = datetime.date.today()

    def set_last_edit_by(self, user, propagate=False):
        if propagate:
            self.propagate_set_value('last_edit_by', user)
        else:
            self.last_edit_by = user

    def set_created_by(self, user, propagate=False):
        if propagate:
            self.propagate_set_value('created_by', user)
        else:
            self.created_by = user

    def approve(self, propagate=True):
        if propagate:
            self.propagate_set_value('approved', True)
        else:
            self.approved = True

    def md_abstract(self):
        return pandoc.convert_md_to_html(self.abstract_text)

    def md_method(self):
        return pandoc.convert_md_to_html(self.method_text)

    def add_keyword(self, keyword):
        if not isinstance(keyword, Keyword):
            raise TypeError("`keyword` must be a Keyword instance.")
        self.keywords.add(keyword)

    def add_identifier(self, instance):
        if not isinstance(instance, ExternalIdentifier):
            raise TypeError(
                "`instance` must be an ExternalIdentifier instance.")

        if isinstance(instance, SraIdentifier):
            self.sra_ids.add(instance)
        elif isinstance(instance, PubmedIdentifier):
            self.pmid_ids.add(instance)
        elif isinstance(instance, DoiIdentifier):
            self.doi_ids.add(instance)
        else:
            raise TypeError(
                "Unsupported class `{}` for `instance`.".format(
                    type(instance).__name__
                ))

    def clear_m2m(self, field_name):
        getattr(self, field_name).clear()

    def clear_doi_ids(self):
        self.clear_m2m('doi_ids')

    def clear_sra_ids(self):
        self.clear_m2m('sra_ids')

    def clear_pubmed_ids(self):
        self.clear_m2m('pmid_ids')