import ckan.plugins as plugins
import ckan.plugins.toolkit as toolkit
import ckan.logic as logic
import ckan.lib.base as base
import metropulse as mp
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

        geog_level = ''
        data_family = ''
        data_category = ''
        data_subcategory = ''
        data_field = ''
       
        if len(pkg_dict['extras']) > 0 and toolkit.c.action == 'read' and toolkit.request.path.split("/")[1] == 'dataset':   
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

            GEOG_LEVEL_NOT_FOUND_ALERT = 'Error: Geographical Level Not Found'
            DATA_FAMILY_NOT_FOUND_ALERT = 'Error: Data Family Not Found'
            ID_DOES_NOT_MATCH_ALERT = 'Error: ID Does Not Match Other Selections'
     
            here = os.path.dirname(__file__)
            rootdir = os.path.dirname(os.path.dirname(here))
            
            geogLevelsFile = open(os.path.join(rootdir, 'MetroPulseGeogLevels.xml'), 'r')
            geogLevelsXml = geogLevelsFile.read()

            fieldsFile = open(os.path.join(rootdir, 'MetroPulseFields.xml'), 'r')
            fieldsXml = fieldsFile.read()
           
            if geog_level != '':
                geogLevelsList = mp.getFilteredChildren(geogLevelsXml, "geoglevels", ('id', 'name'))
                toolkit.c.cmap_geographical_level = GEOG_LEVEL_NOT_FOUND_ALERT
                for i, v in enumerate(geogLevelsList):
                    if v[0] == geog_level:
                        toolkit.c.cmap_geographical_level = v[1]
                        break
            else:
                toolkit.c.cmap_geographical_level = ''

            if data_family != '':
                metalist = mp.getFilteredChildren(fieldsXml, "data", ('id', 'caption'))
                toolkit.c.cmap_data_family = DATA_FAMILY_NOT_FOUND_ALERT
                for i, v in enumerate(metalist):
                    if v[0] == data_family:
                        toolkit.c.cmap_data_family = v[1]
                        break
            else:
                toolkit.c.cmap_data_family = ''
            
            if data_category != '':
                attributeRegEx = {'id': data_family}
                metalist = mp.getFilteredChildren(fieldsXml, "datafamily", ('id', 'caption'), attributeRegEx)
                toolkit.c.cmap_data_category = ID_DOES_NOT_MATCH_ALERT
                for i, v in enumerate(metalist):
                    if v[0] == data_category:
                        toolkit.c.cmap_data_category = v[1]
                        break
            else:
                toolkit.c.cmap_data_category = ''

            if data_subcategory != '':
                attributeRegEx = {'id': data_category}
                metalist = mp.getFilteredChildren(fieldsXml, "datacat", ('id', 'caption'), attributeRegEx)
                toolkit.c.cmap_data_subcategory = ID_DOES_NOT_MATCH_ALERT
                for i, v in enumerate(metalist):
                    if v[0] == data_subcategory:
                        toolkit.c.cmap_data_subcategory = v[1]
                        break
            else:
                toolkit.c.cmap_data_subcategory = ''

            if data_field != '':
                attributeRegEx = {'id': data_subcategory}
                metalist = mp.getFilteredChildren(fieldsXml, "datasubcat", ('id', 'caption'), attributeRegEx)
                toolkit.c.cmap_data_field = ID_DOES_NOT_MATCH_ALERT
                for i, v in enumerate(metalist):
                    if v[0] == data_field:
                        toolkit.c.cmap_data_field = v[1]
                        break
            else:
                 toolkit.c.cmap_data_field = ''

                            
            #Add resources that use the MetroPulse API
            mp.auto_add_metropulse_resources(geog_level, data_subcategory, data_field, pkg_dict)
       
        return pkg_dict


