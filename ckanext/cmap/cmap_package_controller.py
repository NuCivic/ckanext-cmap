import ckan.plugins as plugins
import ckan.plugins.toolkit as toolkit
import ckan.logic as logic
import ckan.lib.base as base
import metropulse
import os

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
        # group's image_url and website_url to pkg_dict for the template to
        # use.
        if pkg_dict['groups']:

            # Datasets can actually belong to more than one group, so we just
            # take the first group the package belongs to.
            group_id = pkg_dict['groups'][0]['id']

            # Get the image_url and website_url and add them to pkg_dict.
            context = {'model': base.model, 'session': base.model.Session,
                    'user': toolkit.c.user or toolkit.c.author,
                    'extras_as_string': True}
            group_dict = logic.get_action('group_show')(context,
                    {'id': group_id})
            pkg_dict['group_image_url'] = group_dict.get('image_url', '')
            pkg_dict['group_website_url'] = group_dict.get('website_url', '')
        
        if len(pkg_dict['extras']) > 0:   
            geog_level = ''
            data_family = ''
            data_category = ''
            data_subcategory = ''
            data_field = ''

            for extra in pkg_dict['extras']:
                if extra['key'] == 'cmap_geographical_level':
                    geog_level = extra['value']

                if extra['key'] == 'cmap_data_family':
                    data_family = extra['value']

                if extra['key'] == 'cmap_data_category':
                    data_category = extra['value']

                if extra['key'] == 'cmap_data_subcategory':
                    data_subcategory = extra['value']

                if extra['key'] == 'cmap_data_field':
                    data_field = extra['value']


     
            here = os.path.dirname(__file__)
            rootdir = os.path.dirname(os.path.dirname(here))

            geogLevelsFile = open(os.path.join(rootdir, 'MetroPulseGeogLevels.xml'), 'r')
            geogLevelsXml = geogLevelsFile.read()

            fieldsFile = open(os.path.join(rootdir, 'MetroPulseFields.xml'), 'r')
            fieldsXml = fieldsFile.read()

            GEOG_LEVEL_NOT_FOUND_ALERT = 'Error: Geographical Level Not Found'
            DATA_FAMILY_NOT_FOUND_ALERT = 'Error: Data Family Not Found'
            ID_DOES_NOT_MATCH_ALERT = 'Error: ID Does Not Match Other Selections'
            
            if geog_level != '':
                geogLevelsList = metropulse.getFilteredChildren(geogLevelsXml, "geoglevels", ('id', 'name'))
                toolkit.c.cmap_geographical_level = GEOG_LEVEL_NOT_FOUND_ALERT
                for i, v in enumerate(geogLevelsList):
                    if v[0] == geog_level:
                        toolkit.c.cmap_geographical_level = v[1]
                        break
            else:
                toolkit.c.cmap_geographical_level = ''

            if data_family != '':
                metalist = metropulse.getFilteredChildren(fieldsXml, "data", ('id', 'caption'))
                toolkit.c.cmap_data_family = DATA_FAMILY_NOT_FOUND_ALERT
                for i, v in enumerate(metalist):
                    if v[0] == data_family:
                        toolkit.c.cmap_data_family = v[1]
                        break
            else:
                toolkit.c.cmap_data_family = ''
            
            if data_category != '':
                attributeRegEx = {'id': data_family}
                metalist = metropulse.getFilteredChildren(fieldsXml, "datafamily", ('id', 'caption'), attributeRegEx)
                toolkit.c.cmap_data_category = ID_DOES_NOT_MATCH_ALERT
                for i, v in enumerate(metalist):
                    if v[0] == data_category:
                        toolkit.c.cmap_data_category = v[1]
                        break
            else:
                toolkit.c.cmap_data_category = ''

            if data_subcategory != '':
                attributeRegEx = {'id': data_category}
                metalist = metropulse.getFilteredChildren(fieldsXml, "datacat", ('id', 'caption'), attributeRegEx)
                toolkit.c.cmap_data_subcategory = ID_DOES_NOT_MATCH_ALERT
                for i, v in enumerate(metalist):
                    if v[0] == data_subcategory:
                        toolkit.c.cmap_data_subcategory = v[1]
                        break
            else:
                toolkit.c.cmap_data_subcategory = ''

            if data_field != '':
                attributeRegEx = {'id': data_subcategory}
                metalist = metropulse.getFilteredChildren(fieldsXml, "datasubcat", ('id', 'caption'), attributeRegEx)
                toolkit.c.cmap_data_field = ID_DOES_NOT_MATCH_ALERT
                for i, v in enumerate(metalist):
                    if v[0] == data_field:
                        toolkit.c.cmap_data_field = v[1]
                        break
            else:
                 toolkit.c.cmap_data_field = ''



        '''
        #pkg_dict['cmap_data_category'] = pprint.pformat(pkg_dict)
        toolkit.c.cmap_data_category = pprint.pformat(pkg_dict)

        #pkg_dict['cmap_geographic_level'] 
        #pkg_dict['cmap_data_family'] 
        #pkg_dict['cmap_data_category'] 
        #pkg_dict['cmap_data_subcategory'] 
        #pkg_dict['cmap_data_field'] 
        
        #toolkit.c.display_values = {}
        #toolkit.c.display_values['cmap_data_category'] = {}
        #toolkit.c.display_values['cmap_data_category']['ARTORGFINA'] = 'foobar'
        '''

        return pkg_dict
