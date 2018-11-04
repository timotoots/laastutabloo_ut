import ckan.plugins as plugins
import ckan.plugins.toolkit as toolkit
import ujson
import urllib2

class ConverterPlugin(plugins.SingletonPlugin):
    plugins.implements(plugins.IConfigurer)

    # IConfigurer

    def update_config(self, config_):
        toolkit.add_template_directory(config_, 'templates')
        toolkit.add_public_directory(config_, 'public')
        toolkit.add_resource('fanstatic', 'converter')
    
    def get():
        request = urllib2.Request('http:/data.laastutabloo.ee/api/action/user_list')
        response_dict = ujson.loads(urllib2.urlopen(request, '{}').read())
        print response_dict
