from django.http import HttpRequest
from django.urls import reverse_lazy
from django.db import transaction

from accounts.permissions import assign_user_as_instance_admin

from core.tasks import send_admin_email
from core.utilities.versioning import track_changes

from ..forms.experiment import ExperimentForm, ExperimentEditForm
from ..models.experiment import Experiment

from .base import (
    DatasetModelView, CreateDatasetModelView, UpdateDatasetModelView
)


class ExperimentDetailView(DatasetModelView):
    """
    object in question and render a simple template for public viewing, or
    Simple class-based detail view for an `Experiment`. Will either find the
    404.

    Parameters
    ----------
    urn : :class:`HttpRequest`
        The urn of the `Experiment` to render.
    """
    # Overriding from `DatasetModelView`.
    # -------
    model = Experiment
    template_name = 'dataset/experiment/experiment.html'
    # -------

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        instance = self.get_object()
        keywords = set([kw for kw in instance.keywords.all()])
        if instance.children:
            for child in instance.children:
                keywords |= set([kw for kw in child.keywords.all()])
        context['keywords'] = sorted(keywords, key=lambda kw: kw.text)
        return context


class ExperimentCreateView(CreateDatasetModelView):
    """
    This view serves up the form:
        - `ExperimentForm` for the instantiation of an Experiment instnace.

    A new experiment instance will only be created if all forms pass validation
    otherwise the forms with the appropriate errors will be served back. Upon
    success, the user is redirected to the newly created experiment page.

    Parameters
    ----------
    request : :class:`HttpRequest`
        The request object that django passes into all views.
    """
    # Overridden from `CreateDatasetModelView`
    # -------
    form_class = ExperimentForm
    template_name = 'dataset/experiment/new_experiment.html'
    model_class_name = 'Experiment'
    # -------

    forms = {"experiment_form": ExperimentForm}

    @transaction.atomic
    def save_forms(self, forms):
        experiment_form = forms['experiment_form']
        experiment = experiment_form.save(commit=True)
        # Save and update permissions. If no experimentset was selected,
        # by default a new experimentset is created with the current user
        # as it's administrator.
        user = self.request.user
        assign_user_as_instance_admin(user, experiment)
        experiment.set_created_by(user, propagate=False)
        experiment.set_modified_by(user, propagate=False)
        experiment.save(save_parents=False)
        track_changes(user, experiment)

        if not self.request.POST['experimentset']:
            assign_user_as_instance_admin(user, experiment.experimentset)
            send_admin_email(self.request.user, experiment.experimentset)
            propagate = True
            save_parents = True
        else:
            propagate = False
            save_parents = False

        experiment.set_created_by(user, propagate=propagate)
        experiment.set_modified_by(user, propagate=propagate)
        experiment.save(save_parents=save_parents)
        track_changes(user, experiment.experimentset)
        track_changes(user, experiment)
        send_admin_email(self.request.user, experiment)
        self.kwargs['urn'] = experiment.urn
        return forms

    def get_experiment_form_kwargs(self, key):
        return {'user': self.request.user}

    def get_success_url(self):
        return "{}{}".format(
            reverse_lazy("dataset:scoreset_new"),
            "?experiment={}".format(self.kwargs['urn'])
        )


class ExperimentEditView(UpdateDatasetModelView):
    """
    This view serves up the form:
        - `ExperimentForm` for the instantiation of an Experiment instnace.

    A new experiment instance will only be created if all forms pass validation
    otherwise the forms with the appropriate errors will be served back. Upon
    success, the user is redirected to the newly created experiment page.

    Parameters
    ----------
    request : :class:`HttpRequest`
        The request object that django passes into all views.
    """
    # Overridden from `CreateDatasetModelView`
    # -------
    form_class = ExperimentForm
    template_name = 'dataset/experiment/update_experiment.html'
    model_class_name = 'Experiment'
    model_class = Experiment
    # -------

    forms = {"experiment_form": ExperimentForm}
    restricted_forms = {"experiment_form": ExperimentEditForm}

    @transaction.atomic
    def save_forms(self, forms):
        experiment_form = forms['experiment_form']
        experiment = experiment_form.save(commit=True)
        experiment.set_modified_by(self.request.user, propagate=False)
        track_changes(self.request.user, experiment)
        self.kwargs['urn'] = experiment.urn
        return forms

    def get_experiment_form_form(self, form_class, **form_kwargs):
        if self.request.method == "POST":
            if self.instance.private:
                return ExperimentForm.from_request(
                    self.request, self.instance, initial=None,
                    prefix=self.prefixes.get('experiment_form', None)
                )
            else:
                return ExperimentEditForm.from_request(
                    self.request, self.instance, initial=None,
                    prefix=self.prefixes.get('experiment_form', None)
                )
        else:
            if 'user' not in form_kwargs:
                form_kwargs.update({'user': self.request.user})
            return form_class(**form_kwargs)
