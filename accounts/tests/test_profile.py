from django.test import TestCase
from django.core import mail
from django.contrib.auth import get_user_model

from guardian.conf.settings import ANONYMOUS_USER_NAME

from dataset.models.experimentset import ExperimentSet
from dataset.models.experiment import Experiment
from dataset.models.scoreset import ScoreSet

from ..models import Profile, user_is_anonymous
from ..permissions import (
    assign_user_as_instance_admin,
    assign_user_as_instance_editor,
    assign_user_as_instance_viewer,
    remove_user_as_instance_admin,
    remove_user_as_instance_editor,
    remove_user_as_instance_viewer
)

User = get_user_model()


class TestUserProfile(TestCase):

    def setUp(self):
        self.exps_1 = ExperimentSet.objects.create()
        self.exps_2 = ExperimentSet.objects.create()
        self.exp_1 = Experiment.objects.create()
        self.exp_2 = Experiment.objects.create()
        self.scs_1 = ScoreSet.objects.create(experiment=self.exp_1)
        self.scs_2 = ScoreSet.objects.create(experiment=self.exp_2)

    def test_can_get_non_anonymous_profiles(self):
        bob = User.objects.create(username="bob", password="secretkey")
        anon = User.objects.get(username=ANONYMOUS_USER_NAME)
        self.assertFalse(user_is_anonymous(bob))
        self.assertTrue(user_is_anonymous(anon))

    def test_profile_gets_users_email_as_default(self):
        bob = User.objects.create(
            username="bob", password="secretkey", email='bob@bob.com')
        self.assertEqual(bob.email, bob.profile.email)

        alice = User.objects.create(
            username="alice", password="secretkey", email="")
        self.assertIsNone(alice.profile.email)

    def test_can_get_full_name(self):
        bob = User.objects.create(
            username="bob", password="secretkey",
            first_name="daniel", last_name="smith"
        )
        self.assertEqual(bob.profile.get_full_name(), "Daniel Smith")

    def test_can_get_short_name(self):
        bob = User.objects.create(
            username="bob", password="secretkey",
            first_name="daniel", last_name="smith"
        )
        self.assertEqual(bob.profile.get_short_name(), "Smith, D")

    def test_send_email_uses_profile_by_email_by_default(self):
        bob = User.objects.create(
            username="bob", password="secretkey",
            first_name="daniel", last_name="smith"
        )
        bob.profile.email = "email@email.com"
        bob.profile.save()
        bob.profile.email_user(message="hello", subject="None")
        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].to, [bob.profile.email])

    def test_send_email_uses_user_email_as_backup(self):
        bob = User.objects.create(
            username="bob", password="secretkey",
            first_name="daniel", last_name="smith", email="bob@email.com"
        )
        bob.profile.email = None
        bob.profile.save()

        bob.profile.email_user(message="hello", subject="None")
        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].to, [bob.email])

    def test_email_user_sends_no_email_if_no_email_present(self):
        bob = User.objects.create(
            username="bob", password="secretkey",
            first_name="daniel", last_name="smith",
            email="",
        )
        bob.profile.email = None
        bob.profile.save()
        bob.profile.email_user(message="hello", subject="None")
        self.assertEqual(len(mail.outbox), 0)

    def test_name_methods_default_to_username(self):
        bob = User.objects.create(username="bob", password="secretkey")
        self.assertEqual(bob.profile.get_full_name(), "bob")
        self.assertEqual(bob.profile.get_short_name(), "bob")

    def test_can_create_user_profile(self):
        bob = User.objects.create(username="bob", password="secretkey")
        self.assertEqual(len(Profile.non_anonymous_profiles()), 1)

    def test_cannot_create_user_profile_twice(self):
        bob = User.objects.create(username="bob", password="secretkey")
        bob.save()  # send another save signal
        self.assertEqual(len(Profile.non_anonymous_profiles()), 1)

    # ----- ExperimentSets
    def test_can_get_all_experimentsets_user_is_admin_on(self):
        bob = User.objects.create(username="bob")
        assign_user_as_instance_admin(bob, self.exps_1)
        assign_user_as_instance_editor(bob, self.exps_2)
        bobs_exps = bob.profile.administrator_experimentsets()
        self.assertEqual(len(bobs_exps), 1)
        self.assertEqual(bobs_exps[0], self.exps_1)

    def test_can_get_all_experimentsets_user_is_editor_on(self):
        bob = User.objects.create(username="bob")
        assign_user_as_instance_editor(bob, self.exps_1)
        assign_user_as_instance_admin(bob, self.exps_2)
        bobs_exps = bob.profile.editor_experimentsets()
        self.assertEqual(len(bobs_exps), 1)
        self.assertEqual(bobs_exps[0], self.exps_1)

    def test_can_get_all_experimentsets_user_is_viewer_on(self):
        bob = User.objects.create(username="bob")
        assign_user_as_instance_viewer(bob, self.exps_1)
        assign_user_as_instance_admin(bob, self.exps_2)
        bobs_exps = bob.profile.viewer_experimentsets()
        self.assertEqual(len(bobs_exps), 1)
        self.assertEqual(bobs_exps[0], self.exps_1)

    # ----- Experiments
    def test_can_get_all_experiments_user_is_admin_on(self):
        bob = User.objects.create(username="bob")
        assign_user_as_instance_admin(bob, self.exp_1)
        assign_user_as_instance_editor(bob, self.exp_2)
        bobs_exp = bob.profile.administrator_experiments()
        self.assertEqual(len(bobs_exp), 1)
        self.assertEqual(bobs_exp[0], self.exp_1)

    def test_can_get_all_experiments_user_is_editor_on(self):
        bob = User.objects.create(username="bob")
        assign_user_as_instance_editor(bob, self.exp_1)
        assign_user_as_instance_admin(bob, self.exp_2)
        bobs_exp = bob.profile.editor_experiments()
        self.assertEqual(len(bobs_exp), 1)
        self.assertEqual(bobs_exp[0], self.exp_1)

    def test_can_get_all_experiments_user_is_viewer_on(self):
        bob = User.objects.create(username="bob")
        assign_user_as_instance_viewer(bob, self.exp_1)
        assign_user_as_instance_admin(bob, self.exp_2)
        bobs_exp = bob.profile.viewer_experiments()
        self.assertEqual(len(bobs_exp), 1)
        self.assertEqual(bobs_exp[0], self.exp_1)

    # ----- ScoreSets
    def test_can_get_all_scoresets_user_is_admin_on(self):
        bob = User.objects.create(username="bob")
        assign_user_as_instance_admin(bob, self.scs_1)
        assign_user_as_instance_editor(bob, self.scs_2)
        bobs_scs = bob.profile.administrator_scoresets()
        self.assertEqual(len(bobs_scs), 1)
        self.assertEqual(bobs_scs[0], self.scs_1)

    def test_can_get_all_scoresets_user_is_editor_on(self):
        bob = User.objects.create(username="bob")
        assign_user_as_instance_editor(bob, self.scs_1)
        assign_user_as_instance_admin(bob, self.scs_2)
        bobs_scs = bob.profile.editor_scoresets()
        self.assertEqual(len(bobs_scs), 1)
        self.assertEqual(bobs_scs[0], self.scs_1)

    def test_can_get_all_scoresets_user_is_viewer_on(self):
        bob = User.objects.create(username="bob")
        assign_user_as_instance_viewer(bob, self.scs_1)
        assign_user_as_instance_admin(bob, self.scs_2)
        bobs_scs = bob.profile.viewer_scoresets()
        self.assertEqual(len(bobs_scs), 1)
        self.assertEqual(bobs_scs[0], self.scs_1)

    # ----- Null values
    def test_empty_list_not_admin_on_anything(self):
        bob = User.objects.create(username="bob")
        self.assertEqual(len(bob.profile.administrator_scoresets()), 0)
        self.assertEqual(len(bob.profile.administrator_experimentsets()), 0)
        self.assertEqual(len(bob.profile.administrator_experiments()), 0)

    def test_empty_list_not_editor_on_anything(self):
        bob = User.objects.create(username="bob")
        self.assertEqual(len(bob.profile.editor_scoresets()), 0)
        self.assertEqual(len(bob.profile.editor_experimentsets()), 0)
        self.assertEqual(len(bob.profile.editor_experiments()), 0)

    def test_empty_list_not_viewer_on_anything(self):
        bob = User.objects.create(username="bob")
        self.assertEqual(len(bob.profile.viewer_scoresets()), 0)
        self.assertEqual(len(bob.profile.viewer_experimentsets()), 0)
        self.assertEqual(len(bob.profile.viewer_experiments()), 0)

    # ----- Remove user
    def test_can_remove_user_as_admin(self):
        bob = User.objects.create(username="bob")
        assign_user_as_instance_admin(bob, self.exps_1)
        self.assertEqual(len(bob.profile.administrator_experimentsets()), 1)

        remove_user_as_instance_admin(bob, self.exps_1)
        self.assertEqual(len(bob.profile.administrator_experimentsets()), 0)

    def test_can_remove_user_as_editor(self):
        bob = User.objects.create(username="bob")
        assign_user_as_instance_editor(bob, self.exps_1)
        self.assertEqual(len(bob.profile.editor_experimentsets()), 1)

        remove_user_as_instance_editor(bob, self.exps_1)
        self.assertEqual(len(bob.profile.editor_experimentsets()), 0)

    def test_can_remove_user_as_viewer(self):
        bob = User.objects.create(username="bob")
        assign_user_as_instance_viewer(bob, self.exps_1)
        self.assertEqual(len(bob.profile.viewer_experimentsets()), 1)

        remove_user_as_instance_viewer(bob, self.exps_1)
        self.assertEqual(len(bob.profile.viewer_experimentsets()), 0)
