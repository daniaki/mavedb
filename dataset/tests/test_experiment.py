#
# import datetime
#
# from django.contrib.auth.models import Group
# from django.db import IntegrityError
# from django.db.models import ProtectedError
# from django.test import TransactionTestCase
#
# from metadata.models import ExternalIdentifier, Keyword
# from genome.models import TargetOrganism
# from dataset.models import ScoreSet
#
# from ..models import Experiment, ExperimentSet
#
#
# class TestExperiment(TransactionTestCase):
#     """
#     The purpose of this unit test is to test that the database model
#     :py:class:`Experiment`, representing an experiment with associated
#     :py:class:`ScoreSet` objects. We will test correctness of creation,
#     validation, uniqueness, queries and that the appropriate errors are raised.
#     """
#
#     reset_sequences = True
#
#     def setUp(self):
#         pass
#
#
#     def test_publish_updates_published_and_last_edit_dates(self):
#         exp = Experiment.objects.create(
#             target=self.target, wt_sequence=self.wt_seq
#         )
#         exp.publish()
#         self.assertEqual(exp.publish_date, datetime.date.today())
#         self.assertEqual(exp.last_edit_date, datetime.date.today())
#
#     def test_publish_updates_private_to_false(self):
#         exp = Experiment.objects.create(
#             target=self.target, wt_sequence=self.wt_seq
#         )
#         exp.publish()
#         self.assertFalse(exp.private)
#
#     def test_autoassign_accession_in_experimentset(self):
#         expset = ExperimentSet.objects.create()
#
#         self.make_experiment(expset=expset)
#         self.make_experiment(expset=expset)
#
#         exp1 = Experiment.objects.all()[0]
#         exp2 = Experiment.objects.all()[1]
#         self.assertEqual(exp1.accession, self.exp_accession_1)
#         self.assertEqual(exp2.accession, self.exp_accession_2)
#
#     def test_cannot_create_accessions_with_duplicate_accession(self):
#         self.make_experiment(acc=self.exp_accession_1)
#         with self.assertRaises(IntegrityError):
#             self.make_experiment(acc=self.exp_accession_1)
#
#     def test_cannot_create_experiment_null_target(self):
#         with self.assertRaises(IntegrityError):
#             Experiment.objects.create(
#                 experimentset=ExperimentSet.objects.create(),
#                 wt_sequence=self.wt_seq
#             )
#
#     def test_cannot_create_experiment_null_wt_seq(self):
#         with self.assertRaises(IntegrityError):
#             Experiment.objects.create(
#                 experimentset=ExperimentSet.objects.create(),
#                 target=self.target
#             )
#
#     def test_experiments_sorted_by_most_recent(self):
#         expset = ExperimentSet.objects.create()
#         date_1 = datetime.date.today()
#         date_2 = datetime.date.today() + datetime.timedelta(days=1)
#         exp_1 = Experiment.objects.create(
#             experimentset=expset,
#             target=self.target,
#             wt_sequence=self.wt_seq,
#             creation_date=date_1)
#         exp_2 = Experiment.objects.create(
#             experimentset=expset,
#             target=self.target,
#             wt_sequence=self.wt_seq,
#             creation_date=date_2)
#         self.assertEqual(
#             exp_2.accession, Experiment.objects.all()[0].accession)
#
#     def test_new_experiment_has_todays_date_by_default(self):
#         self.make_experiment()
#         exp = Experiment.objects.all()[0]
#         self.assertEqual(exp.creation_date, datetime.date.today())
#
#     def test_experiment_and_its_parent_assigned_all_permission_groups(self):
#         self.make_experiment()
#         self.assertEqual(Group.objects.count(), 6)
#
#     def test_experiment_not_approved_and_private_by_default(self):
#         self.make_experiment()
#         exp = Experiment.objects.all()[0]
#         self.assertFalse(exp.approved)
#         self.assertTrue(exp.private)
#
#     def test_cannot_delete_experiment_with_scoresets(self):
#         exp = self.make_experiment()
#         scs = ScoreSet.objects.create(experiment=exp)
#         with self.assertRaises(ProtectedError):
#             exp.delete()
#
#     def test_can_autoassign_scoreset_accession(self):
#         exp = self.make_experiment()
#         scs = ScoreSet.objects.create(experiment=exp)
#         expected = exp.accession.replace(
#             exp.ACCESSION_PREFIX, scs.ACCESSION_PREFIX
#         ) + ".1"
#         self.assertEqual(scs.accession, expected)
#
#     def test_delete_does_not_rollback_scoreset_accession(self):
#         exp = self.make_experiment()
#         scs = ScoreSet.objects.create(experiment=exp)
#         scs.delete()
#         scs = ScoreSet.objects.create(experiment=exp)
#         expected = exp.accession.replace(
#             exp.ACCESSION_PREFIX, scs.ACCESSION_PREFIX
#         ) + ".2"
#         self.assertEqual(scs.accession, expected)
#
#     def test_can_remove_keywords_during_update(self):
#         exp = exp = self.make_experiment()
#         kw1 = Keyword.objects.create(text="test1")
#         kw2 = Keyword.objects.create(text="test2")
#         exp.keywords.add(kw1)
#         exp.update_keywords([kw2])
#         self.assertEqual(exp.keywords.count(), 1)
#         self.assertEqual(exp.keywords.all()[0], kw2)
#
#     def test_can_external_accessions_during_update(self):
#         exp = self.make_experiment()
#         acc1 = ExternalIdentifier.objects.create(text="test1")
#         acc2 = ExternalIdentifier.objects.create(text="test2")
#         exp.external_accessions.add(acc1)
#         exp.update_external_accessions([acc2])
#         self.assertEqual(exp.external_accessions.count(), 1)
#         self.assertEqual(exp.external_accessions.all()[0], acc2)
#
#     def test_can_update_target_organism(self):
#         exp = self.make_experiment()
#         to1 = TargetOrganism.objects.create(text="test1")
#         to2 = TargetOrganism.objects.create(text="test2")
#         exp.target_organism.add(to1)
#         exp.update_target_organism(to2)
#         self.assertEqual(exp.target_organism.count(), 1)
#         self.assertEqual(exp.target_organism.all()[0], to2)