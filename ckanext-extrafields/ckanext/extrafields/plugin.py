import ckan.plugins as plugins
import ckan.plugins.toolkit as toolkit
import pycountry

country_vocab = 'country_names'

def country_names():
    # Create the tag vocabulary if it doesn't exist
    user = toolkit.get_action('get_site_user')({'ignore_auth': True}, {})
    context = {'user': user['name']}
    try: # Check if the vocab exists
        data = {'id': country_vocab}
        toolkit.get_action('vocabulary_show')(context, data)
    except toolkit.ObjectNotFound: # It doesn't exist, create the vocab
        data = {'name': country_vocab}
        vocab = toolkit.get_action('vocabulary_create')(context, data)
        country_names = [country.alpha3 for country in list(pycountry.countries)]
        for name in country_names:
            data = {'name': name, 'vocabulary_id': vocab['id']}
            toolkit.get_action('tag_create')(context, data)

    try:
        countries = toolkit.get_action('tag_list')(data_dict={'vocabulary_id': country_vocab})
        return countries
    except:
        toolkit.ObjectNotFound
        logging.debug('Could not find vocabulary')

class ExtrafieldsPlugin(plugins.SingletonPlugin, toolkit.DefaultDatasetForm):
    plugins.implements(plugins.IDatasetForm)
    plugins.implements(plugins.IPackageController, inherit=True)
    plugins.implements(plugins.IConfigurer)
    plugins.implements(plugins.ITemplateHelpers)
    plugins.implements(plugins.IFacets)

    
    def before_search(self, search_params):
        if search_params.has_key('facet.field') and ('vocab_country_names' not in search_params['facet.field']):
            search_params['facet.field'].append('vocab_country_names')
        return search_params

    # ITemplateHelpers
    def get_helpers(self):
        return {'country_codes': country_names}

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
                toolkit.get_converter('convert_to_tags')(country_vocab)
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

        schema['tags']['__extras'].append(toolkit.get_converter('free_tags_only'))

        schema.update({
            'country_code': [
                toolkit.get_converter('convert_from_tags')(country_vocab),
                toolkit.get_validator('ignore_missing')]
        })
        return schema

    def is_fallback(self):
        return True

    def package_types(self):
        return []

    # IFacets
    def dataset_facets(self, facets_dict, package_type):
        facets_dict['vocab_country_names'] = plugins.toolkit._('Countries')
        return facets_dict

    def group_facets(self, facets_dict, group_type, package_type):
        facets_dict['vocab_country_names'] = plugins.toolkit._('Countries')
        return facets_dict

    def organization_facets(self, facets_dict, organization_type, package_type):
        facets_dict['vocab_country_names'] = plugins.toolkit._('Countries')
        return facets_dict
