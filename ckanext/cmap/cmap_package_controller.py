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

    def before_view(self, pkg_dict):

        # If the dataset (package) being viewed belongs to a group, add that
        # group's image_url to pkg_dict for the template to use.
        if pkg_dict['groups']:

            # Datasets can actually belong to more than one group, so we just
            # take the first group the package belongs to.
            group_id = pkg_dict['groups'][0]['id']

            # Get the image_url and add it to pkg_dict.
            context = {'model': base.model, 'session': base.model.Session,
                    'user': toolkit.c.user or toolkit.c.author}
            group_dict = logic.get_action('group_show')(context,
                    {'id': group_id})
            pkg_dict['group_image_url'] = group_dict['image_url']

        return pkg_dict
