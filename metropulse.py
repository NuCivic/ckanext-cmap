import xml.etree.ElementTree as ET
import re

MP_DOMAIN = 'http://data.cmap.illinois.gov'
MP_CHART_BASE = MP_DOMAIN + '/chart/cmapchart.html?GeogKey=&ContainerList=17043&ContainerLevel=CO&IncludeArchive=True&ChartType=COLUMN&ValidChartTypes=LINE,COLUMN'
MP_GRID_BASE = MP_DOMAIN + '/cmapdatagrid.html?GeogKey=&ContainerLevel=CO&ContainerList=17031&IncludeArchive=True'
MP_MAP_BASE = MP_DOMAIN + '/map/map.html?GeogKey=&ContainerLevel=CO&ContainerList=17031'
MP_HTML_BASE = MP_DOMAIN + '/DEV/API/HTTPGET/GetCmapData.aspx?GeogKey=&ContainerLevel=CO&ContainerList=17031&ReturnFormat=HTMLRESULT'
MP_XML_BASE = MP_DOMAIN + '/API/Rest/XML/guestkey/Data?Containerlevel=CO&Containerlist=17031'
MP_META_BASE = MP_DOMAIN + '/DEV/SYSMAINT/Metadata.aspx?treelevel=4'

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
                r = re.compile(regex)
                if (not r.match(e.get(attr))):
                    match = False

            if (match):
                for c in e.getchildren():
                    rxml.append((c.get(returnAttrib[0]), c.get(returnAttrib[1])))

    return rxml


