"""
Utility functions for  data harvesting

Commandline usage can fire API calls with an ID e.g. 

dc.py organization_purge hscic
"""
import ConfigParser
import json
import sys
import logging
import ffs
from ffs.contrib import http
import ckanapi

inifile = ffs.Path.here()/'../config.ini'
CONF = ConfigParser.ConfigParser()
CONF.read(inifile)

ckan = ckanapi.RemoteCKAN(CONF.get('ckan', 'url'),  apikey=CONF.get('ckan', 'api_key'))

class Error(Exception): 
    def __init__(self, msg):
        Exception.__init__(self, '\n\n\n{0}\n\n\n'.format(msg))

class NHSEnglandNotFoundException(Error): pass

def tags(*tags):
    """
    Given a list of tags as positional arguments TAGS, return
    a list of dictionaries in the format that the CKAN API 
    wants!
    """
    return [{'name': t.replace("'", "") } for t in tags]

def fh_for_url(url):
    """
    Return a file-like-object for URL!
    """
    return http.HTTPPath(url).open()


def _org_existsp(name):
    orglist = ckan.action.organization_list()
    return name in orglist
        

def ensure_publisher(name):
    """
    Ensure that the publisher NAME exists. 
    if not, attempt to create it from our settings file or COMPLAIN LOUDLY!
    """
    if _org_existsp(name):
        return # YAY
    if not CONF.has_section('publisher:'+name):
        what = 'Publisher "{0}" does not exist in the catalogue or inifile'.format(name)
        raise NHSEnglandNotFoundException(what)

    ckan.action.organization_create(
        name=CONF.get('publisher:'+name, 'name'),
        title=CONF.get('publisher:'+name, 'title'),
        description=CONF.get('publisher:'+name, 'description'),
        image_url= CONF.get('publisher:'+name, 'image_url')
    )
    return

class Dataset(object):
    """
    Not really a class. 

    Namespaces are one honking...
    """
    @staticmethod
    def create_or_update(**deets):
        resources = deets.pop('resources')
        try:
            pkg =  ckan.action.package_show(id=deets['name'])
            pkg.update(deets)
            ckan.action.package_update(**pkg)
        except ckanapi.errors.NotFound:
            pkg = ckan.action.package_create(**deets)    

        logging.info(json.dumps(pkg, indent=2))
        for resource in resources:
            resource['package_id'] = pkg['id']
            name = resource['name']
            existing = [r for r in pkg['resources'] if r['name'] == name]
            if not existing:
                ckan.action.resource_create(**resource)
            else:
                existing = existing[0]
                existing.update(resource)
                ckan.action.resource_update(**existing)
        return


if __name__ == '__main__':
    getattr(ckan.action, sys.argv[-2])(id=sys.argv[-1])
