from django.test import TestCase, RequestFactory

from main.models import Licence

from accounts.factories import UserFactory
from accounts.permissions import assign_user_as_instance_admin

from dataset.factories import ExperimentWithScoresetFactory
from dataset import utilities

from ..views import search_view


class TestSearchView(TestCase):

    def setUp(self):
        self.factory = RequestFactory()
        self.path = '/search/'
        self.exp1 = ExperimentWithScoresetFactory()
        self.exp2 = ExperimentWithScoresetFactory()
        self.exp3 = ExperimentWithScoresetFactory()
        self.scs1 = self.exp1.scoresets.first()
        self.scs2 = self.exp2.scoresets.first()
        self.scs3 = self.exp3.scoresets.first()

        self.scs1 = utilities.publish_dataset(self.scs1)
        self.scs2 = utilities.publish_dataset(self.scs2)
        self.scs3 = utilities.publish_dataset(self.scs3)

        self.exp1.refresh_from_db()
        self.exp2.refresh_from_db()
        self.exp3.refresh_from_db()

    def test_private_entries_for_user_have_private_in_name(self):
        user = UserFactory()
        self.exp1.private = True
        self.exp1.add_administrators(user)
        self.scs1.add_administrators(user)
        self.scs1.private = True

        self.exp1.save()
        self.scs1.save()

        request = self.factory.get(self.path)
        request.user = user
        response = search_view(request)

        self.assertContains(response, self.exp1.urn + ' [Private]')
        self.assertContains(response, self.scs1.urn + ' [Private]')

    def test_can_search_by_user_AND_dataset_fields(self):
        user = UserFactory()
        self.exp1.add_administrators(user)
        self.exp2.add_administrators(user)
        self.scs1.add_viewers(user)
        self.exp1.title = 'Hello world'
        self.scs1.title = 'Hello world'
        self.scs1.save()
        self.exp1.save()

        assign_user_as_instance_admin(user, self.exp1)
        request = self.factory.get(
            self.path + '/?username={}&title={}'.format(
                user.username, self.exp1.title))
        request.user = user

        response = search_view(request)
        self.assertContains(response, self.exp1.urn + '/')
        self.assertNotContains(response, self.exp2.urn + '/')
        self.assertNotContains(response, self.exp3.urn + '/')

        self.assertContains(response, self.scs1.urn + '/')
        self.assertNotContains(response, self.scs2.urn + '/')
        self.assertNotContains(response, self.scs3.urn + '/')

    def test_search_all_searches_all_fields_using_OR(self):
        self.exp2.title = 'Hello world'
        self.scs2.title = 'hello world foo bar'
        self.scs2.save()
        self.exp2.save()

        user = UserFactory()
        self.exp1.add_administrators(user)
        self.scs1.add_administrators(user)
        request = self.factory.get(
            self.path + '/?search={}&search={}'.format(
                user.username, self.exp2.title))

        response = search_view(request)
        self.assertContains(response, self.exp1.urn + '/')
        self.assertContains(response, self.exp2.urn + '/')
        self.assertNotContains(response, self.exp3.urn + '/')

        self.assertContains(response, self.scs1.urn + '/')
        self.assertContains(response, self.scs2.urn + '/')
        self.assertNotContains(response, self.scs3.urn + '/')

    def test_comma_sep_input_is_split(self):
        self.exp1.title = "reallyreallylongword"
        self.exp2.title = "reallyreallylongword,anotherreallyreallylongword"
        self.exp3.title = ""
    
        self.scs1.title = 'anotherreallyreallylongword'
        self.scs2.title = ""
        self.scs3.title = ""
        
        self.scs1.save()
        self.scs2.save()
        self.scs3.save()
        self.exp1.save()
        self.exp2.save()
        self.exp3.save()

        request = self.factory.get(
            self.path + '/?search={}'.format(self.exp2.title)
        )

        response = search_view(request)
        self.assertContains(response, self.exp1.urn + '/')
        self.assertContains(response, self.exp2.urn + '/')
        self.assertNotContains(response, self.exp3.urn + '/')

        self.assertContains(response, self.scs1.urn + '/')
        self.assertNotContains(response, self.scs2.urn + '/')
        self.assertNotContains(response, self.scs3.urn + '/')

    def test_double_quoted_comma_sep_not_split_input(self):
        self.exp1.title = "foo bar"
        self.exp2.title = '"Hello,world"'
        self.scs1.title = 'foo bar'
        
        self.scs1.title = 'foo bar'
        self.scs2.title = "Hello"
        self.scs3.title = "World"
        
        self.scs1.save()
        self.scs2.save()
        self.scs3.save()
        self.exp1.save()
        self.exp2.save()
        self.exp3.save()

        request = self.factory.get(
            self.path + '?search={}%2C{}'.format(
                self.exp1.title,
                self.exp2.title)
        )

        response = search_view(request)
        self.assertContains(response, self.exp1.urn + '/')
        self.assertContains(response, self.exp2.urn + '/')
        self.assertNotContains(response, self.exp3.urn + '/')

        self.assertContains(response, self.scs1.urn + '/')
        self.assertNotContains(response, self.scs2.urn + '/')
        self.assertNotContains(response, self.scs3.urn + '/')

    def test_search_empty_returns_all_public_and_private_viewable(self):
        request = self.factory.get(self.path + '/?search=')
        response = search_view(request)
        self.assertContains(response, self.exp1.urn + '/')
        self.assertContains(response, self.exp2.urn + '/')
        self.assertContains(response, self.exp3.urn + '/')

        self.assertContains(response, self.scs1.urn + '/')
        self.assertContains(response, self.scs2.urn + '/')
        self.assertContains(response, self.scs3.urn + '/')

    def test_can_search_by_licence(self):
        self.scs1.licence = Licence.get_cc0()
        self.scs2.licence = Licence.get_cc_by_nc_sa()
        self.scs3.licence = Licence.get_cc_by_nc_sa()
        self.scs1.save()
        self.scs2.save()
        self.scs3.save()

        request = self.factory.get(self.path + '/?licence={}'.format(
            Licence.get_cc0().long_name
        ))
        response = search_view(request)
        self.assertContains(response, self.exp1.urn + '/')
        self.assertNotContains(response, self.exp2.urn + '/')
        self.assertNotContains(response, self.exp3.urn + '/')

        self.assertContains(response, self.scs1.urn + '/')
        self.assertNotContains(response, self.scs2.urn + '/')
        self.assertNotContains(response, self.scs3.urn + '/')
        
    def test_generic_search_searches_by_user(self):
        user1 = UserFactory()
        user2 = UserFactory()
        user2.first_name = 'Ronaldo'
        user2.last_name = 'Romania'
        user2.save()
        
        self.exp1.add_administrators(user1)
        self.exp2.add_administrators(user2)
        request = self.factory.get(
            self.path + '/?search={}'.format(user1.profile.get_full_name()))

        response = search_view(request)
        self.assertContains(response, self.exp1.urn + '/')
        self.assertNotContains(response, self.exp2.urn + '/')
