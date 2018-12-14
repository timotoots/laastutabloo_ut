# encoding: utf-8

from logging import getLogger
from ckan.common import json, config
import ckan.plugins as p
import ckan.plugins.toolkit as toolkit
from lxml import etree
from ckan.common import config
import pandas

FILESTORAGE_PATH = config.get('ckan.storage_path')
log = getLogger(__name__)
ignore_empty = p.toolkit.get_validator('ignore_empty')
natural_number_validator = p.toolkit.get_validator('natural_number_validator')
Invalid = p.toolkit.Invalid

def xml(file_path):
    tree = ET.parse(file_path)

    data = []
    tmp = {}
    for i in tree.iterfind('./*'):
        for j in i.iterfind('*'):
            tmp[j.tag] = j.text
        data.append(tmp)
        tmp = {}

    return pandas.DataFrame(data)

def json(file_path):
    return pandas.read_json(file_path)

def csv(file_path):
    return pandas.read_csv(file_path)

class EditorPlugin(p.SingletonPlugin):
    '''
    This extension views resources using a Editor view.
    '''
    p.implements(p.IConfigurer, inherit=True)
    p.implements(p.IResourceView, inherit=True)


    def info(self):
        return {'name': 'editor',
                'title': 'Editor',
                'filterable': True,
                'icon': 'file',
                'requires_datastore': False,
                'default_title': p.toolkit._('Editor'),
                }

    def update_config(self, config):
        '''
        Set up the resource library, public directory and
        template directory for the view
        '''
        toolkit.add_public_directory(config, 'public')
        toolkit.add_template_directory(config, 'templates')
        toolkit.add_resource('fanstatic', 'editor')

    def can_view(self, data_dict):
        resource = data_dict['resource']
        resource_format = resource.get('format', None)
        if resource_format:
            return resource_format.lower() in ['xml', 'csv', 'json']
        else:
            return False

    def view_template(self, context, data_dict):
        return 'base.html'

    def setup_template_variables(self, context, data_dict):
        resource = data_dict['resource']
        file_type = resource["format"]
        file_id = resource['id']
        file_path = FILESTORAGE_PATH + "/resources/" + file_id[:3] + "/" + file_id[3:6] + "/" + file_id[6:]
        # Pass dataset to js
        data = open(file_path, 'r').read()

        if file_type=='XML':
            data = xml(file_path)
        elif file_type=='JSON':
            data = json(file_path)
        elif file_type=='CSV':
            res = data.split(",")
            data = []
            for i in res:
                data.append({"text": i
                })             
        else:
    	      print "Not a valid file type"

        # Fetch current user's api_key and pass it to js
        api_key = toolkit.get_action('user_show')(context, {'id': toolkit.c.userobj.id})['apikey']
        dataset_id = toolkit.c.id
        return {'data': data, 'api_key': api_key, 'dataset_id': dataset_id, 'resource_id': file_id}
