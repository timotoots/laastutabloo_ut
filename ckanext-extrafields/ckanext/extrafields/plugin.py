import ckan.plugins as p
import ckan.plugins.toolkit as tk


class ExtrafieldsPlugin(p.SingletonPlugin, tk.DefaultDatasetForm):
	p.implements(p.IDatasetForm)
	p.implements(p.IConfigurer)

	def _modify_package_schema(self, schema):
		schema.update({
			'custom_text': [tk.get_validator('ignore_missing'),
			tk.get_converter('convert_to_extras')]
		})
		schema['resources'].update({
			'custom_resource_text' : [ tk.get_validator('ignore_missing'),
			tk.get_converter('convert_to_extras')]
		})
		return schema

	def show_package_schema(self):
		schema = super(ExtrafieldsPlugin, self).show_package_schema()
		schema.update({
			'custom_text': [tk.get_converter('convert_from_extras'),
			tk.get_converter('convert_to_extras')]
		})
		schema['resources'].update({
			'custom_resource_text' : [ tk.get_validator('ignore_missing'),
			tk.get_converter('convert_to_extras')]
		})
		return schema

	def update_config(self, config):
		tk.add_template_directory(config, 'templates')

	def is_fallback(self):
		return True

	def package_types(self):
		return []
