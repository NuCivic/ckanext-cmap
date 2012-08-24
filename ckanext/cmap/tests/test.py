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

        # A test sysadmin user.
        cls.testsysadmin = ckan.model.User.get('testsysadmin')

        # Some test normal users.
        cls.annafan = ckan.model.User.get('annafan')
        cls.russianfan = ckan.model.User.get('russianfan')
        cls.tester = ckan.model.User.get('tester')

        # Test datasets.
        cls.warandpeace = ckan.model.Package.get('warandpeace')
        cls.annakarenina = ckan.model.Package.get('annakarenina')

    @classmethod
    def teardownClass(cls):
        ckan.model.repo.rebuild_db()

    def test_01_add_organization_button_not_logged_in(self):
        # Test that the "Add an Organization" button doesn't show when not
        # logged in.
        offset = routes.url_for(controller='group', action='index')
        response = self.app.get(offset)
        assert "Add an Organization" not in response
        assert "/organization/new" not in response

    def test_01_add_organization_button_logged_in(self):
        # Test that the "Add an Organization" button doesn't show when a
        # non-sysadmin user is logged in.
        offset = routes.url_for(controller='group', action='index')
        extra_environ = {'Authorization': str(self.annafan.apikey)}
        response = self.app.get(offset, extra_environ=extra_environ)
        assert "Add an Organization" not in response
        assert "/organization/new" not in response

    def test_01_add_organization_button_sysadmin_logged_in(self):
        # Test that the "Add an Organization" button shows when a sysadmin is
        # logged in.
        offset = routes.url_for(controller='group', action='index')
        extra_environ = {'Authorization': str(self.testsysadmin.apikey)}
        response = self.app.get(offset, extra_environ=extra_environ)
        assert "Add an Organization" in response
        assert "/organization/new" in response

    def test_01_add_org_via_api_not_logged_in(self):
        # Test that not-logged-in users can't create organizations via the API.
        params = {'name': 'my_new_organization'}
        response = self.app.post('/api/action/group_create',
            params=json.dumps(params), status=403).json
        assert response['success'] is False
        assert response['error']['message'] == 'Access denied'

    def test_01_add_org_via_api_not_sysadmin(self):
        # Test that non-sysadmin users can't create organizations via the API.
        params = {'name': 'my_new_organization'}
        extra_environ = {'Authorization': str(self.annafan.apikey)}
        response = self.app.post('/api/action/group_create',
            params=json.dumps(params), extra_environ=extra_environ,
            status=403).json
        assert response['success'] is False
        assert response['error']['message'] == 'Access denied'

    def test_01_add_org_via_api_sysadmin(self):
        # Test that sysadmin users can create organizations via the API.
        params = {'name': 'my_new_organization'}
        extra_environ = {'Authorization': str(self.testsysadmin.apikey)}
        response = self.app.post('/api/action/group_create',
            params=json.dumps(params), extra_environ=extra_environ).json
        assert response['success'] is True
        assert response['result']['name'] == 'my_new_organization'
    
    # TODO: Test creating orgs via v1 and v2 APIs.

    def _check_group_read_page(self, response, name, title, description,
            group_type, website, logo):
        assert response.status == 200
        assert response.req.url.endswith('/organization/{}'.format(name))
        assert group_type in response
        assert description in response

        # Test the organization's logo.
        soup = BeautifulSoup(response.body)
        img = soup.find('img', src=logo)
        assert img, "Organization's logo should appear on organization's page"
        assert img.get('alt', None) == title, ("Organization's logo should "
            "have organization's title as alt text")
        assert img.find_parents('a', href=website), ("Organization's logo "
                "should be hyperlinked to organization's website")

        assert len(soup.find_all('a', href=website)) == 2, ("There should be "
                "two links to the organization's website (text link and logo "
                "linked to website")

    def test_01_create_group(self):
        # Test creating a group, including the group type, website URL and
        # image URL fields.

        # First get the new organisation form.
        offset = routes.url_for(controller='group', action='new')
        extra_environ = {'Authorization': str(self.testsysadmin.apikey)}
        response = self.app.get(offset, extra_environ=extra_environ)
        # The group edit form is the second form (after the search form).
        form = response.forms[1]

        # Fill out the form and submit it.
        form['name'] = 'my_test_organization'
        form['title'] = 'My Test Organization'
        form['description'] = 'my description'
        form['cmap_group_type'] = 'Municipality'
        form['website_url'] = 'http://sisinmaru.blog17.fc2.com/'
        form['image_url'] = 'http://mikecane.files.wordpress.com/2007/03/kitten.jpg'
        response = form.submit('save', extra_environ=extra_environ)

        # The response from submitting the form should be a 302 redirect.
        assert response.status == 302
        response = response.follow(extra_environ=extra_environ)

        # It should have redirected us to the read page for the organization
        # we just created.
        self._check_group_read_page(response,
                name='my_test_organization',
                title='My Test Organization',
                description='my description',
                group_type='Municipality',
                website='http://sisinmaru.blog17.fc2.com/',
                logo='http://mikecane.files.wordpress.com/2007/03/kitten.jpg')

    def test_02_update_group(self):
        # Test updating a group, including the group type, website URL and
        # image URL fields.

        offset = routes.url_for(controller='group', action='edit', 
                id='my_test_organization')
        extra_environ = {'Authorization': str(self.testsysadmin.apikey)}
        response = self.app.get(offset, extra_environ=extra_environ)
        form = response.forms[1]
        form['description'] = 'updated description'
        form['cmap_group_type'] = 'County'
        form['website_url'] = 'http://duckduckgo.com/'
        form['image_url'] = 'http://mousebreath.com/wp-content/uploads/2011/08/maru__02.jpg'
        response = form.submit('save', extra_environ=extra_environ)
        assert response.status == 302
        response = response.follow(extra_environ=extra_environ)
        self._check_group_read_page(response,
                name='my_test_organization',
                title='My Test Organization',
                description='updated description',
                group_type='County',
                website='http://duckduckgo.com/',
                logo='http://mousebreath.com/wp-content/uploads/2011/08/maru__02.jpg'
                )

    def test_02_group_with_no_logo(self):
        # Test creating and reading a group with a website but no logo.
        pass

    def test_02_group_with_no_website(self):
        # Test creating and reading a group with a logo but no website.
        pass

    def test_02_group_with_no_website_or_logo(self):
        # Test creating and reading a group with no website or logo.
        pass

    def test_02_join_organization(self):
        # Test a user joining an organization and then editing the
        # organization, adding datasets to the organization.
        pass

    def test_02_group_with_datasets(self):
        # Create a group, add some datasets to the group, check that datasets
        # show on group read page, update the group, check that datasets still
        # show on group read page.
        # Use some datasets with resources and some without.
        # Check the view counts next to the datasets.
        pass

    def test_03_create_dataset(self):
        # Fill in the add dataset form and submit, test the values on the
        # dataset read page.
        # Include filling in the CMAP custom metadata fields and testing their
        # display values.
        # Include a test that the organization's logo appears on the dataset's
        # page (with the organization's title as alt text, and hyperlinked to
        # the Organization's website.
        # Test adding a dataset to an org with both a website and a logo, one
        # with a website but no logo, a logo but no website, and neither
        # website nor logo, each time test the dataset read page.
        pass
    
    def test_03_create_dataset_without_org(self):
        # Test that it's not possible to submit the add dataset form without
        # giving an org.
        pass

    def test_03_update_dataset_without_org(self):
        # Test that it's not possible to submit the update dataset form without
        # giving an org.
        pass

    def test_03_create_dataset_without_org_api(self):
        # Test that it's not possible to create a dataset with no organization
        # via the API.
        pass

    def test_03_update_dataset_without_org_api(self):
        # Test that it's not possible to update a dataset to have no org via
        # the API.
        pass

    def test_04_update_dataset(self):
        # Get the edit form for the dataset created in the previous test, edit
        # some of its values (e.g. tags) including CMAP's custom fields, test
        # the dataset read page.
        pass
    
    def test_05_move_dataset(self):
        # Testing updating a dataset and moving it from one organization to
        # another.
        pass

    def test_06_front_page(self):
        # Test the front page, including looking for the datasets and their
        # tracking values, and looking for the list of groups.
        pass

    def test_06_test_sort(self):
        # Test using the search and sort ordering options.
        pass

    def test_06_search_from_inner_page(self):
        # Test that the search form works from pages other than the front page.
        pass

    def test_06_admin_link(self):
        # Test the admin link. Should appear at top of site, but only when an
        # admin is logged in, should link to /ckan-admin.
        pass
