import ckan.plugins as plugins

class CMAPRoutingPlugin(plugins.SingletonPlugin):
    '''Plugin that adds ckanext-cmap's custom routes.'''

    plugins.implements(plugins.IRoutes, inherit=True)

    def before_map(self, mapper):
        # Make CKAN's search page (which would normally appear at /dataset)
        # appear at the root URL.
        mapper.connect('home', '/', controller='package', action='search')
        return mapper
