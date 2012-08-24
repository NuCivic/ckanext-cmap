import xml.etree.ElementTree as ET
import re
import sys
import urllib2
import urlparse
import json

MP_DOMAIN = 'http://data.cmap.illinois.gov'
MP_CHART_BASE = MP_DOMAIN + '/chart/cmapchart.html?GeogKey=&ContainerList=17043&ContainerLevel=CO&IncludeArchive=True&ChartType=COLUMN&ValidChartTypes=LINE,COLUMN'
MP_GRID_BASE = MP_DOMAIN + '/cmapdatagrid.html?GeogKey=&ContainerLevel=CO&ContainerList=17031&IncludeArchive=True'
MP_MAP_BASE = MP_DOMAIN + '/map/map.html?GeogKey=&ContainerLevel=CO&ContainerList=17031'
MP_HTML_BASE = MP_DOMAIN + '/DEV/API/HTTPGET/GetCmapData.aspx?GeogKey=&ContainerLevel=CO&ContainerList=17031&ReturnFormat=HTMLRESULT'
MP_XML_BASE = MP_DOMAIN + '/API/Rest/XML/guestkey/Data?Containerlevel=CO&Containerlist=17031'
MP_META_BASE = MP_DOMAIN + '/DEV/SYSMAINT/Metadata.aspx?treelevel=4'


URL_TYPES = ['chart', 'grid', 'map', 'html', 'xml', 'meta']



#BASE_URL = "http://localhost/api"
#API_KEY= "8b3bb2f9-4651-4982-965e-cb274ccdcf67"

BASE_URL = "http://opendata.cmap.illinois.gov/"
# CMAP DEV SERVER ADMIN API KEY
API_KEY="18910fe5-2208-43a2-8b3e-6eef9758481c"


def auto_add_metropulse_resources(geog_level, data_subcategory, data_field, pkg_dict):

    if geog_level != '' and data_subcategory != '' and data_field != '':         
        metropulse_metadata = {'GeogLevel': geog_level, 
                  'DataSubcategory': data_subcategory, 
                   'DataField': data_field}

        metropulse_urls = getMetroPulseAssetURLs(metropulse_metadata) 

        #TAKE THIS OUT#
        #for m in metropulse_urls.keys():
        #    metropulse_urls[m] = 'http://www.testdomain.com'
        #END TAKE THIS OUT
       
        resource_update_list = {}

        for resource in pkg_dict['resources']:
            for t in URL_TYPES:
                if resource['name'] == t: 
                    if t in metropulse_urls: 
                        if resource['url'] == metropulse_urls[t]:
                            metropulse_urls.pop(t)                
                        else:
                            resource_update_list[t] = resource['id']
                
        for url_type, url in metropulse_urls.iteritems(): 
            pkg_dict_create = {}
            pkg_dict_create['name'] = url_type
            pkg_dict_create['description'] = 'MetroPulse ' + url_type 
            pkg_dict_create['url'] = url
            pkg_dict_create['package_id'] = pkg_dict['id']

            if url_type in resource_update_list:                                            
                api_action = 'resource_update'
                pkg_dict_create['id'] = resource_update_list[url_type]
            else:
                api_action = 'resource_create'

            response = post_to_ckan_api(action=api_action,
                base_url=BASE_URL, data=pkg_dict_create, api_key=API_KEY)



def post_to_ckan_api(action, base_url, data=None, api_key=None):
    '''Post a data dict to one of the actions of the CKAN action API.

    See the documentation of the action API, including each of the available
    actions and the data dicts they accept, here:
    
        http://docs.ckan.org/en/ckan-1.8/apiv3.html

    :param action: the action to post to, e.g. "package_create"
    :type action: string
    
    :param data: the data to post (optional, default: {})
    :type data: dictionary

    :param api_key: the CKAN API key to put in the 'Authorization' header of
        the HTTP request (optional, default: None)
    :type api_key: string

    :returns: the dictionary returned by the CKAN API, a dictionary with three
        keys 'success' (True or False), 'help' (the docstring for the action
        posted to) and 'result' in the case of a successful request or 'error'
        in the case of an unsuccessful request
    :rtype: dictionary

    '''
    if data is None:
        # Even if you don't want to post any data to the CKAN API, you still
        # have to send an empty dict.
        data = {}
    path = '/api/action/{action}'.format(action=action)
    url = urlparse.urljoin(base_url, path)
    request = urllib2.Request(url)
    if api_key is not None:
        request.add_header('Authorization', api_key)
    try:
        response = urllib2.urlopen(request, json.dumps(data))
        # The CKAN API returns a dictionary (in the form of a JSON string)
        # with three keys 'success' (True or False), 'result' and 'help'.
        d = json.loads(response.read())
        assert d['success'] is True
        return d
    except urllib2.HTTPError, e:
        # For errors, the CKAN API also returns a dictionary with three
        # keys 'success', 'error' and 'help'.
        error_string = e.read()
        try:
            # Load the JSON returned by CKAN as a Python dictionary.
            d = json.loads(error_string)
                
            if type(d) is unicode:
                # Sometimes CKAN returns an erros as a JSON string not a dict,
                # gloss over it here.
                return {'success': False, 'help': '', 'error': d}

            assert d['success'] is False
            return d
        except ValueError:
            # Sometimes CKAN returns a string that is not JSON, lets gloss
            # over it.
            return {'success': False, 'error': error_string, 'help': ''}


def getMetroPulseAssetURLs(paramDict):
    # Usage: paramDict has 3 keys: 
    # GeogLevel, 
    # DataSubcategory, 
    # and DataField
    # These should be set to the values passed by the dataset form. 
    # getMetroPulseAssetURLs returns six urls, one for the MetroPulse 
    # chart, grid, map, html, xml, and metadata.

    urls = {}
    params = ''
    for k, v in paramDict.iteritems():
         params += '&' + k + '=' + v
         if k == 'DataField':
              id = '&ID=' + v


    urls['chart'] = MP_CHART_BASE + params
    urls['grid'] = MP_GRID_BASE + params
    urls['map'] = MP_MAP_BASE + params
    urls['html'] = MP_HTML_BASE + params
    #For meta and xml, the datafield param is called 'id'
    urls['xml'] = MP_XML_BASE + params + id
    urls['meta'] = MP_META_BASE + params + id


    return urls



'''NOTE: xml.etree.Element.getiterator and .getchildren will break on upgrade to python 2.7'''


def getFilteredChildren(xmlString, tag, returnAttrib, attributeRegEx = {}):
    tree = ET.fromstring(xmlString)
    elems = tree.getiterator(tag)
    rxml = []

    for e in elems:
        if (e.tag == tag):
            match = True
            for attr, regex in attributeRegEx.iteritems():
                if regex == '':
                    match = False
                    break

                r = re.compile(regex)
                if (not r.match(e.get(attr))):
                    match = False

            if (match):
                for c in e.getchildren():
                    rxml.append((c.get(returnAttrib[0]), c.get(returnAttrib[1])))

    return rxml


