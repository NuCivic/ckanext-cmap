import os
import ckan.plugins as plugins

class CMAPConfigurerPlugin(plugins.SingletonPlugin):
    '''Plugin that adds ckanext-cmap's custom config settings.'''

    plugins.implements(plugins.IConfigurer, inherit=True)

    def update_config(self, config):
        # Add ckanext-cmap's public and template dirs to the extra_public_paths
        # and extra_template_paths config settings.
        here = os.path.dirname(__file__)
        template_dir = os.path.join(here, 'templates')
        config['extra_template_paths'] = ','.join([template_dir, config.get('extra_template_paths', '')])
        public_dir = os.path.join(here, 'public')
        config['extra_public_paths'] = ','.join([public_dir, config.get('extra_public_paths', '')])
