import ckan.plugins as plugins
import ckan.plugins.toolkit as tk
import ckan.logic.action as action
import filter

class ConverterPlugin(plugins.SingletonPlugin):
    plugins.implements(plugins.IResourceController)
    
    def before_create(self, context, resource):
	filter.filter(ressource)

    def after_create(self, context, resource):
        print context
        print
        print resource
        

    def before_update(self, context, current, resource):
        pass

    def after_update(self, context, resource):
        pass

    def before_delete(self, context, resource, resources):
        pass

    def after_delete(self, context, resources):
        pass

    def before_show(self, resource):
        pass
        #print resource
        

