import ckan.plugins as plugins
import ckan.plugins.toolkit as toolkit
import helpers


class ExtrafieldsPlugin(plugins.SingletonPlugin, toolkit.DefaultDatasetForm):
    plugins.implements(plugins.IDatasetForm)
    plugins.implements(plugins.IPackageController, inherit=True)
    plugins.implements(plugins.IConfigurer)
    plugins.implements(plugins.ITemplateHelpers)
    plugins.implements(plugins.IFacets)

    # IPackageController
    def before_search(self, search_params):
        if search_params.has_key('facet.field') and ('vocab_country_names' not in search_params['facet.field']):
            search_params['facet.field'].append('vocab_country_names')
        return search_params

    def after_search(self, search_results, search_params):
        facets = search_results.get('search_facets')
        if not facets or 'release_date' not in facets:
            return search_results
        
        for item in facets['release_date']['items']:
            item['display_name'] = item['display_name'][:4] # Take first 4 characters

        return search_results

    # ITemplateHelpers
    def get_helpers(self):
        return {'country_codes': helpers.country_names,
                'country_code_to_name': helpers.country_code_to_name,
                'country_options': helpers.country_options,
                'topics': helpers.topics,
                'topic_options': helpers.topic_options,
                'regions': helpers.regions,
                'region_code_to_name': helpers.region_code_to_name,
                'region_options': helpers.region_options,
                'statuses': helpers.statuses,
                'status_options': helpers.status_options,
                }

    # IConfigurer
    def update_config(self, config_):
        toolkit.add_template_directory(config_, 'templates')
        toolkit.add_public_directory(config_, 'public')
        toolkit.add_resource('fanstatic', 'extrafields')

    # IDatasetForm
    def _modify_package_schema(self, schema):
        from validators import (not_both_empty, year, yyyy_or_dd_mon_yyyy,
                                max_items)
        not_missing = toolkit.get_validator('not_missing')
        not_empty = toolkit.get_validator('not_empty')
        ignore_missing = toolkit.get_validator('ignore_missing')
        convert_to_tags = toolkit.get_converter('convert_to_tags')
        convert_to_extras = toolkit.get_converter('convert_to_extras')
        schema.update({
            'title': [not_empty, unicode],
            'notes': [not_empty, unicode],
            'topic': [
                not_empty,
                max_items(3),
                convert_to_tags(helpers.topic_vocab)
            ],
            'country_code': [
                not_both_empty('region', 'region'),
                convert_to_tags(helpers.country_vocab)
            ],
            'region': [
                not_both_empty('country_code', 'country'),
                convert_to_tags(helpers.region_vocab)
            ],
            'status': [
                ignore_missing,
                convert_to_extras
            ],
            'ref_system': [
                ignore_missing,
                convert_to_extras
            ],
            'release_date': [
                ignore_missing,
                year,
                convert_to_extras
            ],
            'start_date': [
                ignore_missing,
                yyyy_or_dd_mon_yyyy,
                convert_to_extras
            ],
            'end_date': [
                ignore_missing,
                yyyy_or_dd_mon_yyyy,
                convert_to_extras
            ],
            'group': [
                ignore_missing,
                convert_to_extras
            ],
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
            'topic': [
                toolkit.get_converter('convert_from_tags')(
                    helpers.topic_vocab),
                toolkit.get_validator('ignore_missing')],
            'country_code': [
                toolkit.get_converter('convert_from_tags')(
                    helpers.country_vocab),
                toolkit.get_validator('ignore_missing')],
            'region': [
                toolkit.get_converter('convert_from_tags')(
                    helpers.region_vocab),
                toolkit.get_validator('ignore_missing')],
            'status': [
                toolkit.get_converter('convert_from_extras'),
                toolkit.get_validator('ignore_missing')],
            'ref_system': [
                toolkit.get_converter('convert_from_extras'),
                toolkit.get_validator('ignore_missing')],
            'release_date': [
                toolkit.get_converter('convert_from_extras'),
                toolkit.get_validator('ignore_missing')],
            'start_date': [
                toolkit.get_converter('convert_from_extras'),
                toolkit.get_validator('ignore_missing')],
            'end_date': [
                toolkit.get_converter('convert_from_extras'),
                toolkit.get_validator('ignore_missing')],
            'group': [
                toolkit.get_converter('convert_from_extras'),
                toolkit.get_validator('ignore_missing')],
        })
        return schema

    def is_fallback(self):
        return True

    def package_types(self):
        return []

    # IFacets
    def dataset_facets(self, facets_dict, package_type):
        facets_dict['vocab_country_names'] = plugins.toolkit._('Countries')
        facets_dict['vocab_regions'] = plugins.toolkit._('Region')
        facets_dict.pop('tags')
        facets_dict['vocab_topics'] = plugins.toolkit._('Topic')
        facets_dict['release_date'] = plugins.toolkit._('Published Date')
        
        order = [
            'vocab_country_names', 
            'vocab_regions', 
            'release_date',
            'vocab_topics', 
            'organization', 
            'groups',
            'res_format', 
            'license_id'
        ]
        # Ensure order
        for key in order:
            data = facets_dict[key]
            facets_dict.pop(key)
            facets_dict[key] = data
        return facets_dict

    def group_facets(self, facets_dict, group_type, package_type):
        facets_dict['vocab_country_names'] = plugins.toolkit._('Countries')
        return facets_dict

    def organization_facets(self, facets_dict, organization_type, package_type):
        facets_dict['vocab_country_names'] = plugins.toolkit._('Countries')
        return facets_dict

