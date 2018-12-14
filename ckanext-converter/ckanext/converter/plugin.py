import ckan.plugins as plugins
import filter

class ConverterPlugin(plugins.SingletonPlugin):
    
    # Has to implement all the methods for IResourceController
    plugins.implements(plugins.IResourceController)
    
    # Filter received resource after upload
    def after_create(self, context, resource):
        pass#filter.filter(context, resource)
    
    # Not needed, so not changed
    def before_create(self, context, resource):
        pass
        
    # Not needed, so not changed
    def before_update(self, context, current, resource):
        pass
    
    # Not needed, so not changed
    def after_update(self, context, resource):
        if !resource['name'].endswith("_converted"):
            filter.filter(context, resource)
    
    # Not needed, so not changed
    def before_delete(self, context, resource, resources):
        pass
    
    # Not needed, so not changed
    def after_delete(self, context, resources):
        pass

    # Not needed, so not changed
    def before_show(self, resource):
        pass
        

