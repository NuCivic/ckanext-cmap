import ckan
import paste.fixture
import pylons.test
import routes
from ckan.tests.html_check import HtmlCheckMethods
from ckan.lib.helpers import json

class TestCMAP(HtmlCheckMethods):
    '''Unit tests for ckanext-cmap's custom features.

    '''
    @classmethod
    def setupClass(cls):
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

    def test_add_organization_button_not_logged_in(self):
        # Test that the "Add an Organization" button doesn't show when not
        # logged in.
        offset = routes.url_for(controller='group', action='index')
        response = self.app.get(offset)
        assert "Add an Organization" not in response
        assert "/organization/new" not in response

    def test_add_organization_button_logged_in(self):
        # Test that the "Add an Organization" button doesn't show when a
        # non-sysadmin user is logged in.
        offset = routes.url_for(controller='group', action='index')
        extra_environ = {'Authorization': str(self.annafan.apikey)}
        response = self.app.get(offset, extra_environ=extra_environ)
        assert "Add an Organization" not in response
        assert "/organization/new" not in response

    def test_add_organization_button_sysadmin_logged_in(self):
        # Test that the "Add an Organization" button shows when a sysadmin is
        # logged in.
        offset = routes.url_for(controller='group', action='index')
        extra_environ = {'Authorization': str(self.testsysadmin.apikey)}
        response = self.app.get(offset, extra_environ=extra_environ)
        assert "Add an Organization" in response
        assert "/organization/new" in response

    def test_add_org_via_api_not_logged_in(self):
        # Test that not-logged-in users can't create organizations via the API.
        params = {'name': 'my_new_organization'}
        response = self.app.post('/api/action/group_create',
            params=json.dumps(params), status=403).json
        assert response['success'] is False
        assert response['error']['message'] == 'Access denied'

    def test_add_org_via_api_not_sysadmin(self):
        # Test that non-sysadmin users can't create organizations via the API.
        params = {'name': 'my_new_organization'}
        extra_environ = {'Authorization': str(self.annafan.apikey)}
        response = self.app.post('/api/action/group_create',
            params=json.dumps(params), extra_environ=extra_environ,
            status=403).json
        assert response['success'] is False
        assert response['error']['message'] == 'Access denied'

    def test_add_org_via_api_sysadmin(self):
        # Test that sysadmin users can create organizations via the API.
        params = {'name': 'my_new_organization'}
        extra_environ = {'Authorization': str(self.testsysadmin.apikey)}
        response = self.app.post('/api/action/group_create',
            params=json.dumps(params), extra_environ=extra_environ).json
        assert response['success'] is True
        assert response['result']['name'] == 'my_new_organization'
    
    # TODO: Test creating orgs via v1 and v2 APIs.
