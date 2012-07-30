import ckan.plugins as plugins
import ckan.plugins.toolkit as toolkit
import ckan.logic as logic
import ckan.lib.base as base

class CMAPPackageController(plugins.SingletonPlugin):
    plugins.implements(plugins.IPackageController, inherit=True)

    def after_search(self, search_results, search_params):

        # Get all of the site's groups.
        context = {'model': base.model, 'session': base.model.Session,
                'user': toolkit.c.user or toolkit.c.author}
        group_names = logic.get_action('group_list')(context, {})
        group_dicts = []
        for group_name in group_names:
            group_dict = logic.get_action('group_show')(context,
                    {'id': group_name})
            group_dicts.append(group_dict)

        # Add the groups to the template context so the package/search.html
        # template can access them.
        toolkit.c.groups = group_dicts

        return search_results
