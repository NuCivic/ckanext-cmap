import ckan.plugins as plugins
import ckan.lib.helpers as helpers


def get_sort_by_url(order):
    queryvars = dict(plugins.toolkit.request.queryvars)
    if 'sort' in queryvars:
        if queryvars['sort'] == order + ' asc':
            queryvars['sort'] = order + ' desc'
        elif queryvars['sort'] == order + ' desc':
            queryvars['sort'] = order + ' asc'
        else:
            queryvars['sort'] = order + ' asc'
    else:
        queryvars['sort'] = order + ' asc'
    if plugins.toolkit.c.id:
        queryvars['id'] = plugins.toolkit.c.id
    url = helpers.url_for(controller=plugins.toolkit.c.controller,
        action=plugins.toolkit.c.action, **queryvars)
    #url = url.replace('%2B', '+')
    return url


class CMAPHelpers(plugins.SingletonPlugin):
    '''Plugin that adds ckanext-cmap's custom template helper functions.'''

    plugins.implements(plugins.ITemplateHelpers, inherit=True)

    def get_helpers(self):
        return {'get_sort_by_url': get_sort_by_url}
