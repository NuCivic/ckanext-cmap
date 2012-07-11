import os
import ckan.plugins as plugins
import ckan.plugins.toolkit as toolkit
import ckan.logic as logic

class ExamplePlugin(plugins.SingletonPlugin):
    plugins.implements(plugins.IDatasetForm, inherit=True)
    plugins.implements(plugins.IConfigurer, inherit=True)
    plugins.implements(plugins.IRoutes, inherit=True)

    def update_config(self, config):
        here = os.path.dirname(__file__)
        rootdir = os.path.dirname(os.path.dirname(here))
        template_dir = os.path.join(rootdir, 'ckanext', 'cmap', 'templates')
        config['extra_template_paths'] = ','.join([template_dir, config.get('extra_template_paths', '')])
        public_dir = os.path.join(rootdir, 'ckanext', 'cmap', 'public')
        config['extra_public_paths'] = ','.join([public_dir, config.get('extra_public_paths', '')])

    def before_map(self, mapper):
        # This makes CKAN's search page (which would normally appear at
        # /dataset) appear at the root URL.
        mapper.connect('home', '/', controller='package', action='search')
        return mapper

    def package_form(self):
        return 'package/new_package_form.html'

    def new_template(self):
        return 'package/new.html'

    def comments_template(self):
        return 'package/comments.html'

    def search_template(self):
        return 'package/search.html'

    def read_template(self):
        return 'package/read.html'

    def history_template(self):
        return 'package/history.html'

    def is_fallback(self):
        return False

    def package_types(self):
        return ['mpdataset']

    def setup_template_variables(self, context, data_dict=None, package_type=None):
        try:
            data = {'vocabulary_id': u'country_codes'}
            toolkit.c.geographical_coverage = logic.get_action('tag_list')(context, data)
        except logic.NotFound:
            toolkit.c.geographical_coverage = []

    def form_to_db_schema(self, package_type=None):
        from ckan.logic.schema import package_form_schema
        from ckan.lib.navl.validators import ignore_missing
        from ckan.logic.converters import convert_to_tags

        schema = package_form_schema()
        schema.update({
            'geographical_coverage': [ignore_missing, convert_to_tags('country_codes')]
        })
        return schema

    def db_to_form_schema(data, package_type=None):
        from ckan.logic.converters import convert_from_tags, free_tags_only
        from ckan.lib.navl.validators import ignore_missing, keep_extras

        schema = logic.package_form_schema()
        schema.update({
            'tags': {
                '__extras': [keep_extras, free_tags_only]
            },
            'geographical_coverage': [convert_from_tags('country_codes'), ignore_missing],
        })
        return schema
