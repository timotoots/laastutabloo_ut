# encoding: utf-8

from logging import getLogger

from ckan.common import json, config
import ckan.plugins as p
import ckan.plugins.toolkit as toolkit

from lxml import etree
from collections import Counter
from ckan.common import config
import re
FILESTORAGE_PATH = config.get('ckan.storage_path') 

log = getLogger(__name__)
ignore_empty = p.toolkit.get_validator('ignore_empty')
natural_number_validator = p.toolkit.get_validator('natural_number_validator')
Invalid = p.toolkit.Invalid


def get_mapview_config():
    '''
    Extracts and returns map view configuration of the reclineview extension.
    '''
    namespace = 'ckanext.spatial.common_map.'
    return dict([(k.replace(namespace, ''), v) for k, v in config.iteritems()
                 if k.startswith(namespace)])

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
            return resource_format.lower() in ['xml', 'csv', 'xls', 'xlsx', 'tsv', 'json']
        else:
            return False
   
    def view_template(self, context, data_dict):
        return 'base.html'

    def get_helpers(self):
        return {
            'get_map_config': get_mapview_config
        }
        
    def setup_template_variables(self, context, data_dict):
        resource = data_dict['resource']
        filetype = resource["type"]
        file_id = resource['id']
        file_path = FILESTORAGE_PATH + "/resources/" + file_id[:3] + "/" + file_id[3:6] + "/" + file_id[6:]
        root = etree.fromstring(open(file_path, 'r').read())        
        tree = etree.ElementTree(root)
        treeview = ""
        tag_name = ""
        
        for tag in root.iter():
          path = tree.getpath(tag)
          path = path.replace('/', '    ')
          spaces = Counter(path)
          tag_name = path.split()[-1].split('[')[0]
          tag_name = ' ' * (spaces[' '] - 4) + tag_name
          treeview += tag_name + "\n"
        
        return {'root': root, 'tree': tree, 'treeview': treeview}

