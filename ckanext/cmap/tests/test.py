import ckan
import ckan.tests
import paste.fixture
import pylons.test
import routes
from ckan.lib.helpers import json
from bs4 import BeautifulSoup


class TestCMAP:
    '''Unit tests for ckanext-cmap's custom features.'''

    @classmethod
    def setupClass(cls):

        # The app object is a wrapper around the CKAN web application, with
        # methods for making testing convenient.
        # See http://pythonpaste.org/testing-applications.html
        cls.app = paste.fixture.TestApp(pylons.test.pylonsapp)

        # Create CKAN's standard test data (War and Peace, Anna Karenina, etc.)
        ckan.tests.CreateTestData.create()

        # CKAN's standard test sysadmin user.
        cls.testsysadmin = ckan.model.User.get('testsysadmin')

        # CKAN's standard test normal users.
        cls.annafan = ckan.model.User.get('annafan')
        cls.russianfan = ckan.model.User.get('russianfan')
        cls.tester = ckan.model.User.get('tester')

        # CKAN's standard test datasets.
        cls.warandpeace = ckan.model.Package.get('warandpeace')
        cls.annakarenina = ckan.model.Package.get('annakarenina')

        # Some test groups that we will create later.
        cls.test_groups = [
            {'name': "municipality_test_group",
            'title': "Municipality Test Group",
            'description': "Test description",
            'cmap_group_type': "Municipality",
            'website_url': "http://sisinmaru.blog17.fc2.com/",
            'image_url':
                    "http://mikecane.files.wordpress.com/2007/03/kitten.jpg",
            },
            {'name': "county_test_group",
            'title': "County Test Group",
            'description': "Test description",
            'cmap_group_type': "County",
            'website_url': "http://sisinmaru.blog17.fc2.com/",
            'image_url':
                    "http://mikecane.files.wordpress.com/2007/03/kitten.jpg",
            },
            {'name': "test_group_with_no_group_type",
            'title': "Test Group Without Group Type",
            'description': "Test description",
            'website_url': "http://sisinmaru.blog17.fc2.com/",
            'image_url':
                    "http://mikecane.files.wordpress.com/2007/03/kitten.jpg",
            },
            {'name': "test_group_without_image",
            'title': "Test Group Without Image URL",
            'description': "Test description",
            'cmap_group_type': "Other Government",
            'website_url': "http://sisinmaru.blog17.fc2.com/",
            },
            {'name': "test_group_without_website",
            'title': "Test Group Without Website URL",
            'description': "Test description",
            'cmap_group_type': "CMAP Project Team",
            'image_url':
                    "http://mikecane.files.wordpress.com/2007/03/kitten.jpg",
            },
            {'name': "test_group_without_website_or_image",
            'title': "Test Group Without Website or Image",
            'description': "Test description",
            'cmap_group_type': "Nonprofit Organization",
            },
        ]

        # Some test datasets that we will create later.
        # (The top-level keys are the users who will create the datasets.)
        # TODO: Add datasets with different values and missing values for
        # CMAP's custom dataset fields, geographical level, data family, etc.
        # That should increase the number of test datasets.
        cls.test_datasets = {
            'annafan': [
                {'name': "test_dataset",
                'title': "Test Dataset",
                'tag_string': "water quality, pollution, rivers",
                'group': "municipality_test_group",
                },
                {'name': "test_dataset_with_no_tags",
                'title': "Test Dataset",
                'group': "municipality_test_group",
                },
            ]
        }

    @classmethod
    def teardownClass(cls):
        ckan.model.repo.rebuild_db()

    def id_for_group(self, name):
        '''Get a group's ID from the CKAN API.

        Useful because some organizations forms only accept group IDs, not
        names.

        '''
        params = {'id': name}
        response = self.app.post('/api/action/group_show',
            params=json.dumps(params)).json
        assert response['success'] is True
        return response['result']['id']

    def check_group_read_page(self, response, name=None, title=None,
            description=None, cmap_group_type=None, website_url=None,
            image_url=None):
        '''Check the contents of a group read page.

        Given the response from a group read page, tests that the page contains
        the right contents such as the link to the group's website, the group's
        logo, etc.

        '''
        assert response.status == 200
        assert response.req.url.endswith('/organization/{0}'.format(name))

        if cmap_group_type is not None:
            assert cmap_group_type in response, (
                    "cmap_group_type should be shown on group's page")

        if description is not None:
            assert description in response, (
                    "group's description should be shown on group's page")

        soup = BeautifulSoup(response.body)

        if image_url is not None:
            img = soup.find('img', src=image_url)
            assert img, (
                "Organization's logo should appear on organization's page")
            assert img.get('alt', None) == title, ("Organization's logo "
                "should have organization's title as alt text")
            if website_url is not None:
                assert img.find_parents('a', href=website_url), (
                    "Organization's logo should be hyperlinked to "
                    "organization's website")
                assert len(soup.find_all('a', href=website_url)) == 2, (
                    "There should be two links to the organization's website "
                    "(text link and logo linked to website)")
        elif website_url is not None:
            assert len(soup.find_all('a', href=website_url)) == 1, (
                "There should be one link to the organization's website")

    def check_dataset_read_page(self, response, name=None, title=None,
            tag_string=None, group=None, cmap_geographical_level=None,
            cmap_data_family=None, cmap_data_category=None,
            cmap_data_subcategory=None, cmap_data_field=None):
        '''Check the contents of a dataset read page.

        Given the response from a dataset read page, tests that the page
        contains the right contents such as the link to the group's website,
        the group's logo, etc.

        '''

        # Test the the values for ckanext-cmap's custom dataset metadata fields
        # show on the page.
        for metadata_field in (cmap_geographical_level, cmap_data_family,
                cmap_data_category, cmap_data_subcategory, cmap_data_field):
            if metadata_field is not None:
                assert metadata_field in response

        # Test that the logo of the dataset's group shows on the dataset's
        # page, is linked to the group's website, and has the group's title as
        # alt text.
        if group is not None:
            # Get the group from the CKAN API.
            params = {'id': group}
            api_response = self.app.post('/api/action/group_show',
                    params=json.dumps(params)).json
            assert api_response['success'] is True
            image_url = api_response['result'].get('image_url', None)
            website_url = api_response['result'].get('website_url', None)
            group_title = api_response['result'].get('title', None)
            if image_url is not None:
                soup = BeautifulSoup(response.body)
                img = soup.find('img', source=image_url)
                assert img, ("Organization's logo should appear on pages of "
                        "organization's datasets")
                assert img.get('alt', None) == group_title, ("Organization's "
                    "logo should have organization's title as alt text")
                if website_url is not None:
                    assert img.find_parents('a', href=website_url), (
                        "Organization's logo should be hyperlinked to "
                        "organization's website on organization's dataset's "
                        "pages")

    def test_00_add_organization_button_not_logged_in(self):
        '''Test that the "Add an Organization" button doesn't show when not
        logged in.'''
        offset = routes.url_for(controller='group', action='index')
        response = self.app.get(offset)
        assert "Add an Organization" not in response
        assert "/organization/new" not in response

    def test_00_add_organization_button_logged_in(self):
        '''Test that the "Add an Organization" button doesn't show when a
        non-sysadmin user is logged in.'''
        offset = routes.url_for(controller='group', action='index')
        extra_environ = {'Authorization': str(self.annafan.apikey)}
        response = self.app.get(offset, extra_environ=extra_environ)
        assert "Add an Organization" not in response
        assert "/organization/new" not in response

    def test_00_add_organization_button_sysadmin_logged_in(self):
        '''Test that the "Add an Organization" button shows when a sysadmin is
        logged in.'''
        offset = routes.url_for(controller='group', action='index')
        extra_environ = {'Authorization': str(self.testsysadmin.apikey)}
        response = self.app.get(offset, extra_environ=extra_environ)
        assert "Add an Organization" in response
        assert "/organization/new" in response

    def test_00_add_group_via_api_when_not_logged_in(self):
        '''Test that not-logged-in users can't create organizations via the
        API.'''
        params = {'name': 'my_new_organization'}
        response = self.app.post('/api/action/group_create',
            params=json.dumps(params), status=403).json
        assert response['success'] is False
        assert response['error']['message'] == 'Access denied'

    def test_00_add_group_via_api_when_not_sysadmin(self):
        '''Test that non-sysadmin users can't create organizations via the API.
        '''
        params = {'name': 'my_new_organization'}
        extra_environ = {'Authorization': str(self.annafan.apikey)}
        response = self.app.post('/api/action/group_create',
            params=json.dumps(params), extra_environ=extra_environ,
            status=403).json
        assert response['success'] is False
        assert response['error']['message'] == 'Access denied'

    def test_00_add_group_via_api_when_sysadmin(self):
        '''Test that sysadmin users can create organizations via the API.'''
        params = {'name': 'my_new_organization'}
        extra_environ = {'Authorization': str(self.testsysadmin.apikey)}
        response = self.app.post('/api/action/group_create',
            params=json.dumps(params), extra_environ=extra_environ).json
        assert response['success'] is True
        assert response['result']['name'] == 'my_new_organization'

    # TODO: Tests for adding groups via the v1 and v2 APIs.

    def test_00_create_groups(self):
        '''Create the test groups using the new group form.'''

        for group in self.test_groups:
            # Get the 'new group' form.
            offset = routes.url_for(controller='group', action='new')
            # Only sysadmins can create groups.
            extra_environ = {'Authorization': str(self.testsysadmin.apikey)}
            response = self.app.get(offset, extra_environ=extra_environ)
            form = response.forms['group-edit']

            # Fill out the form and submit it.
            for key in group:
                form[key] = group[key]
            response = form.submit('save', extra_environ=extra_environ)

            # The response from submitting the form should be a 302 redirect.
            assert response.status == 302
            response = response.follow(extra_environ=extra_environ)

            # It should have redirected us to the read page for the group
            # we just created.
            assert response.status == 200
            assert response.req.url.endswith('/organization/{0}'.format(
                group['name']))

    # TODO
    def test_create_group_with_invalid_group_type(self):
        '''Test trying to create a group with an invalid cmap_group_type.'''
        pass

    # TODO
    def test_create_group_with_no_group_type(self):
        '''Test trying to create a group with no cmap_group_type.'''
        pass

    def test_01_register_user(self):
        '''Test registering a new user account with the registration form.'''

        # We don't really need to test this, as CMAP hasn't customised user
        # registration at all and the standard CKAN tests include tests for it.
        # But I needed to make another sysadmin user for the rest of the tests
        # anyway and may as well do it this way.

        # Register a new user using the registration form.
        offset = routes.url_for(controller='user', action='register')
        response = self.app.get(offset)
        form = response.forms['user-edit']
        form['name'] = "cmap_sysadmin"
        form['email'] = "cmap_sysadmin@cmap.com"
        form['fullname'] = "Herr. Doktor CMAP Sysadmin"
        form['password1'] = "cmap"
        form['password2'] = "cmap"
        response = form.submit('save')

        # Make cmap_sysadmin a sysadmin user.
        TestCMAP.cmap_sysadmin = ckan.model.User.get('cmap_sysadmin')
        ckan.model.add_user_to_role(self.cmap_sysadmin, ckan.model.Role.ADMIN,
                ckan.model.System())

    def test_02_apply_to_join_group(self):
        '''Test the form for sending an application email to join a group.'''

        extra_environ = {'Authorization': str(self.annafan.apikey)}
        offset = '/organization/apply'
        params = {'id': 'municipality_test_group'}
        response = self.app.post(offset, extra_environ=extra_environ,
                params=json.dumps(params))
        form = response.forms['publisher-edit']
        form['parent'] = self.id_for_group('municipality_test_group')
        form['reason'] = "I really want to join this group"
        response = form.submit('save', extra_environ=extra_environ)
        assert response.status == 200
        # TODO: This gets a "No mail server was found" error, the email server
        # needs to be mocked to test this completely.

    # TODO
    def test_apply_to_join_group_when_not_logged_in(self):
        '''Test applying to join a group when not logged in.'''
        pass

    # TODO
    def test_apply_to_join_group_when_already_a_member(self):
        '''Test applying to join a group that you're already a member of.'''
        pass

    def test_02_add_user_to_group(self):
        '''Test a group admin adding another user to a group.'''

        offset = "/organization/users/municipality_test_group"
        extra_environ = {'Authorization': str(self.testsysadmin.apikey)}
        response = self.app.get(offset, extra_environ=extra_environ)
        form = response.forms['publisher-edit']
        form['users__1__name'] = 'annafan'
        response = form.submit('save', extra_environ=extra_environ)
        # TODO: Read the group and test that user was added.

    # TODO
    def test_02_promote_to_group_admin(self):
        '''Test a group admin promoting a group editor to admin.'''
        pass

    # TODO
    def test_02_demote_to_editor(self):
        '''Test a group admin demoting another admin to editor.'''
        pass

    def test_03_create_datasets(self):
        '''Create the test datasets using the new dataset form.'''

        api_keys = {
            'testsysadmin': str(self.testsysadmin.apikey),
            'cmap_sysadmin': str(self.cmap_sysadmin.apikey),
            'annafan': str(self.annafan.apikey),
            'russianfan': str(self.russianfan.apikey),
            'tester': str(self.tester.apikey),
        }

        for user in self.test_datasets:
            for dataset in self.test_datasets[user]:

                # Get the 'new dataset' form.
                offset = routes.url_for(controller='package', action='new')
                extra_environ = {'Authorization': api_keys[user]}
                response = self.app.get(offset, extra_environ=extra_environ)
                form = response.forms['dataset-edit']

                # Fill out the form and submit it.
                for key in dataset:
                    if key == 'group':
                        form['groups__0__id'] = self.id_for_group(
                                dataset['group'])
                        form['groups__0__capacity'] = 'public'
                    else:
                        form[key] = dataset[key]
                response = form.submit('save', extra_environ=extra_environ)

                # The response from submitting the form should be 302 redirect.
                assert response.status == 302
                response = response.follow(extra_environ=extra_environ)

                # It should have redirected us to the read page for the dataset
                # we just created.
                assert response.status == 200
                assert response.request.url.endswith('/dataset/{0}'.format(
                    dataset['name'])), response.req.url
                # TODO: Test the contents of the page.

    # TODO
    def test_03_create_dataset_with_no_group(self):
        '''Test trying to create a dataset without a group.'''
        pass

    # TODO
    def test_03_create_dataset_with_multiple_groups(self):
        '''Test trying to create a dataset with multiple groups.'''
        pass

    # TODO
    def test_04_add_resources(self):
        '''Test adding some resources to some datasets.'''
        # This test should add some resources to some datasets, and leave some
        # datasets without resources.
        # Might have to use the resource_create action API function,
        # as I'm not sure if the resource edit form can be used with TestApp
        # like we do with the group edit and dataset edit forms above.
        pass

    # TODO
    def test_05_read_datasets(self):
        '''Test the dataset read page for each of the test datasets.'''

        for datasets in self.test_datasets.values():
            for dataset in datasets:
                offset = routes.url_for(controller='package', action='read',
                        id=dataset['name'])
                response = self.app.get(offset)
                self.check_dataset_read_page(response, **dataset)

    def test_05_read_groups(self):
        '''Test the group read page for each of the test groups.'''

        for group in self.test_groups:
            offset = routes.url_for(controller='group', action='read',
                    id=group['name'])
            response = self.app.get(offset)
            self.check_group_read_page(response, **group)

    # TODO
    def test_05_read_users(self):
        '''Test the user read page for each of the test users.'''
        pass

    def test_06_update_group(self):
        '''Test updating some groups.

        Including changing the group type, website URL and image URL fields,
        and then testing that the new values show on the group read page.

        '''
        for group_name in ('municipality_test_group', 'county_test_group'
                'test_group_with_no_group_type', 'test_group_without_image',
                'test_group_without_website',
                'test_group_without_website_or_image'):
            offset = routes.url_for(controller='group', action='edit',
                    id=group_name)
            extra_environ = {'Authorization': str(self.testsysadmin.apikey)}
            response = self.app.get(offset, extra_environ=extra_environ)

            new_description = 'updated description'
            new_group_type = 'County'
            new_website_url = 'http://duckduckgo.com/'
            new_image_url = \
               'http://mousebreath.com/wp-content/uploads/2011/08/maru__02.jpg'

            form = response.forms['group-edit']
            form['description'] = new_description
            form['cmap_group_type'] = new_group_type
            form['website_url'] = new_website_url
            form['image_url'] = new_image_url
            response = form.submit('save', extra_environ=extra_environ)

            assert response.status == 302
            response = response.follow(extra_environ=extra_environ)

            self.check_group_read_page(response,
                    name=group_name,
                    description=new_description,
                    cmap_group_type=new_group_type,
                    website_url=new_website_url,
                    image_url=new_image_url
                    )

    # TODO
    def test_06_update_dataset(self):
        '''Test updating some datasets.

        Including editing ckanext-cmap's custom dataset metadata fields, and
        then checking that the new values show on the dataset read page.

        '''
        pass

   # TODO
    def test_06_move_dataset(self):
        '''Test updating a dataset and moving it from one group to another.

        '''
        pass

    # TODO
    def test_07_front_page(self):
        '''Test the contents of the front page.

        Including looking for the datasets and their tracking values, and
        looking for the list of groups.

        '''
        pass

    # TODO
    def test_07_test_sort(self):
        '''Test using the search and sort ordering options.'''
        pass

    # TODO
    def test_07_search_from_inner_page(self):
        '''Test the search form works from pages other than the front page.'''
        pass

    # TODO
    def test_07_admin_link(self):
        '''Test the admin link.

        The admin link should appear at top of site, but only when an
        admin is logged in, and should link to /ckan-admin.

        '''
        pass

    # TODO
    def test_07_private_dataset(self):
        '''Test private datasets.'''
        pass
