#!/usr/bin/env python
import metropulse
import os
import cgi
import cgitb
import json

form = cgi.FieldStorage()
data_family = form.getvalue("data_family")
data_cat = form.getvalue("data_cat")
data_subcat = form.getvalue("data_subcat")

geogLevelsFile = open('MetroPulseGeogLevels.xml', 'r')
geogLevelsXml = geogLevelsFile.read()

fieldsFile = open('MetroPulseFields.xml', 'r')
fieldsXml = fieldsFile.read()

geogLevelsList = metropulse.getFilteredChildren(geogLevelsXml, "geoglevels", ('id', 'name'))

dataFamilyList = metropulse.getFilteredChildren(fieldsXml, "data", ('id', 'caption'))


# attributeRegEx regular expression narrows future values to ones
# that are children of current values (makes sure selections make sense together)
rlist = ""

if data_family:
    attributeRegEx = {'id': data_family}
    rlist = metropulse.getFilteredChildren(fieldsXml, "datafamily", ('id', 'caption'), attributeRegEx)
elif data_cat:
    attributeRegEx = {'id': data_cat}
    rlist = metropulse.getFilteredChildren(fieldsXml, "datacat", ('id', 'caption'), attributeRegEx)
elif data_subcat:
    attributeRegEx = {'id': data_subcat}   
    rlist = metropulse.getFilteredChildren(fieldsXml, "datasubcat", ('id', 'caption'), attributeRegEx)

rjson = []

for i in rlist:
    rjson.append({"optionValue":i[0], "optionDisplay":i[1]})



print "Content-Type: text/plain"
print "Access-Control-Allow-Origin: *"
#print "Content-Type: application/json"
print
print json.dumps(rjson)

#print '[ {"optionValue":10, "optionDisplay": "Remy"},{"optionValue":11, "optionDisplay": "Arif"},{"optionValue":12, "optionDisplay": "JC"}]'

#print rlist
