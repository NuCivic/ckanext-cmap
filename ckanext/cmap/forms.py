import ckan.plugins as plugins
import ckan.plugins.toolkit as toolkit
import ckan.logic as logic
import ckan.logic.schema
import ckan.logic.converters as converters
import ckan.lib.navl.validators as validators
import ckan.lib.base as base
import ckan.authz as authz
import metropulse
import os

def group_required(key, data, errors, context):
    # We want at least a group in the data we are provided.
    has_group = ('groups', 0, 'id') in data
    if not has_group:
        errors[('Organizations', '')] = [
            toolkit._('Please choose an organization to add the dataset to')]

class CMAPOrganizationForm(plugins.SingletonPlugin):
    '''A plugin that implements ckanext-cmap's custom organization form.

    This is a copy of OrganizationForm from
    ckan/ckanext/organizations/forms.py, with CMAP-specific customisations
    added.

    '''
    plugins.implements(plugins.IGroupForm, inherit=True)
    plugins.implements(plugins.IConfigurer, inherit=True)
    plugins.implements(plugins.IRoutes, inherit=True)

    def before_map(self, map):
        # Map /organizations/* URLs to the custom organization controller.
        controller = 'ckanext.cmap.controllers:CMAPOrganizationController'
        map.connect('/organization/users/{id}', controller=controller,
                    action='users')
        map.connect('/organization/apply/{id}', controller=controller,
                    action='apply')
        map.connect('/organization/apply', controller=controller,
                    action='apply')
        map.connect('/organization/edit/{id}', controller='group',
                    action='edit')
        map.connect('/organization/new', controller='group', action='new')
        map.connect('/organization/{id}', controller='group', action='read')
        map.connect('/organization',  controller='group', action='index')
        map.redirect('/organizations', '/organization')
        return map

    def update_config(self, config):
        # Override /group/* as the default URL prefix gor groups.
        config['ckan.default.group_type'] = 'organization'

    def new_template(self):
        '''Return the path to the template for the new organization page.'''
        return 'organization_new.html'

    def index_template(self):
        '''Return the path to the template for the organization index page.'''
        return 'organization_index.html'

    def read_template(self):
        '''Return the path to the template for the organization read page.'''
        return 'organization_read.html'

    def history_template(self):
        '''
        Return the path to the template for the organization history page.
        '''
        return 'organization_history.html'

    def group_form(self):
        '''Return the path to the template for the organization form.'''
        return 'organization_form.html'

    def group_types(self):
        '''Return the group types that this plugin handles.'''
        return ["organization"]

    def is_fallback(self):
        '''Return true if this plugin is the fallback group plugin.'''
        return False

    def form_to_db_schema(self):
        '''Return the schema for mapping group data from the form to the db.'''
        schema = ckan.logic.schema.group_form_schema()

        # Add CMAP's custom Group Type metadata field to the schema.
        schema.update({
           'cmap_group_type': [validators.ignore_missing, unicode,
               converters.convert_to_extras]
           })

        return schema

    def db_to_form_schema(self):
        '''Return the schema for mapping group data from the db to the form.'''
        schema = ckan.logic.schema.group_form_schema()

        # Add CMAP's custom Group Type metadata field to the schema.
        schema.update({
         'cmap_group_type': [converters.convert_from_extras,
             validators.ignore_missing],
           })

        return schema

    def setup_template_variables(self, context, data_dict):
        toolkit.c.user_groups = toolkit.c.userobj.get_groups('organization')
        local_ctx = {'model': base.model, 'session': base.model.Session,
                     'user': toolkit.c.user or toolkit.c.author}

        try:
            logic.check_access('group_create', local_ctx)
            toolkit.c.is_superuser_or_groupadmin = True
        except logic.NotAuthorized:
            toolkit.c.is_superuser_or_groupadmin = False

        if 'group' in context:
            group = context['group']
            # Only show possible groups where the current user is a member
            toolkit.c.possible_parents = toolkit.c.userobj.get_groups(
                    'organization', 'admin')

            toolkit.c.parent = None
            grps = group.get_groups('organization')
            if grps:
                toolkit.c.parent = grps[0]
            toolkit.c.users = group.members_of_type(base.model.User)

        # Add the options for the custom 'Group Type' metadata field to the
        # template context.
        toolkit.c.cmap_group_types = ("Municipality", "County",
                "Citizen Group")


class CMAPDatasetForm(plugins.SingletonPlugin):
    '''Plugin that implements ckanext-cmap's custom dataset form.

    This is a copy of OrganizationDatasetForm from
    ckan/ckanext/organizations/forms.py, with CMAP-specific customisations
    added.

    '''
    plugins.implements(plugins.IDatasetForm, inherit=True)

    def is_fallback(self):
        return True

    def package_types(self):
        return ['dataset']

    def new_template(self):
        '''Return the path to the template for the new dataset page.'''
        return 'package/new.html'

    def comments_template(self):
        '''Return the path to the template for the comments page.'''
        return 'package/comments.html'

    def search_template(self):
        '''Return the path to the template for the search page.'''
        return 'package/search.html'

    def read_template(self):
        '''Return the path to the template for the read page.'''
        return 'package/read.html'

    def history_template(self):
        '''Return the path to the template for the history page.'''
        return 'package/history.html'

    def package_form(self):
        '''Return the path to the template for the new/edit dataset form.'''
        return 'organization_package_form.html'

    def form_to_db_schema(self):
        schema = ckan.logic.schema.form_to_db_package_schema()

        schema['groups']['capacity'] = [validators.ignore_missing, unicode]
        schema['__after'] = [group_required]

        schema.update({'cmap_geographical_level': [validators.ignore_missing, unicode, converters.convert_to_extras]})

        return schema

    def db_to_form_schema(self):
        schema = ckan.logic.schema.db_to_form_package_schema()

        schema.update({'cmap_geographical_level': [converters.convert_from_extras, validators.ignore_missing]})

        return schema

    def setup_template_variables(self, context, data_dict):
        data_dict.update({'available_only': True})

        toolkit.c.groups_available = toolkit.c.userobj and \
            toolkit.c.userobj.get_groups('organization') or []
        toolkit.c.licences = [('', '')] + base.model.Package.get_license_options()
        toolkit.c.is_sysadmin = authz.Authorizer().is_sysadmin(toolkit.c.user)

        ## This is messy as auths take domain object not data_dict
        context_pkg = context.get('package', None)
        pkg = context_pkg or toolkit.c.pkg
        if pkg:
            try:
                if not context_pkg:
                    context['package'] = pkg
                logic.check_access('package_change_state', context)
                toolkit.c.auth_for_change_state = True
            except logic.NotAuthorized:
                toolkit.c.auth_for_change_state = False

        #Get MetroPulse fields and add them to the form        
        here = os.path.dirname(__file__)
        rootdir = os.path.dirname(os.path.dirname(here))
        
        geogLevelsFile = open(os.path.join(rootdir, 'MetroPulseGeogLevels.xml'), 'r')
        geogLevelsXml = geogLevelsFile.read()

        fieldsFile = open(os.path.join(rootdir, 'MetroPulseFields.xml'), 'r')
        fieldsXml = fieldsFile.read()

        geogLevelsList = metropulse.getFilteredChildren(geogLevelsXml, "geoglevels", ('id', 'name'))
        toolkit.c.cmap_geog_levels = geogLevelsList

