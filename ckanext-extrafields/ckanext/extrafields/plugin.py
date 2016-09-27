import ckan.plugins as plugins
import ckan.plugins.toolkit as toolkit
import pycountry

def country_codes():
    return [country.name for country in list(pycountry.countries)]

class ExtrafieldsPlugin(plugins.SingletonPlugin, toolkit.DefaultDatasetForm):
    plugins.implements(plugins.IDatasetForm)
    plugins.implements(plugins.IConfigurer)
    plugins.implements(plugins.ITemplateHelpers)
    plugins.implements(plugins.IFacets)

    # ITemplateHelpers
    def get_helpers(self):
        return {'country_codes': country_codes}

    # IConfigurer
    def update_config(self, config_):
        toolkit.add_template_directory(config_, 'templates')
        toolkit.add_public_directory(config_, 'public')
        toolkit.add_resource('fanstatic', 'extrafields')

    # IDatasetForm
    def _modify_package_schema(self, schema):
        schema.update({
            'country_code': [
                toolkit.get_validator('ignore_missing'),
                toolkit.get_converter('convert_to_extras')
            ]
        })
        return schema

    def create_package_schema(self):
        schema = super(ExtrafieldsPlugin, self).create_package_schema()
        schema = self._modify_package_schema(schema)
        return schema

    def update_package_schema(self):
        schema = super(ExtrafieldsPlugin, self).update_package_schema()
        schema = self._modify_package_schema(schema)
        return schema

    def show_package_schema(self):
        schema = super(ExtrafieldsPlugin, self).show_package_schema()
        schema.update({
            'country_code': [
                toolkit.get_converter('convert_from_extras'),
                toolkit.get_validator('ignore_missing')]
        })
        return schema

    def is_fallback(self):
        return True

    def package_types(self):
        return []

    # IFacets
    def dataset_facets(self, facets_dict, package_type):
        facets_dict['country_code'] = plugins.toolkit._('Countries')
        return facets_dict