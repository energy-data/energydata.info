from ckan.plugins import toolkit, IConfigurer, ITemplateHelpers, SingletonPlugin, IRoutes, implements, IActions, IPackageController
from urlparse import urlparse
from ckan.logic import check_access
from ckan.logic.action.get import _group_or_org_list

import pylons.config as config

import ckan.plugins.toolkit as toolkit

def is_excluded(org):
    exclusion_list = config.get('ckanext.theme.excluded_org_list').split(' ')
    for item in exclusion_list:
        if (item == org):
            return True
    return False

def organization_list(context, data_dict):
    check_access('organization_list', context, data_dict)
    data_dict['groups'] = data_dict.pop('organizations', [])
    data_dict.setdefault('type', 'organization')
    org_list = _group_or_org_list(context, data_dict, is_org=True)
    org_list = [org for org in org_list if not is_excluded(org)]
    return org_list

def most_recent_datasets():
    ''' Returns three most recently modified datasets'''
    datasets = toolkit.get_action('current_package_list_with_resources')(data_dict={
        'limit': 3
    })
    return datasets

def exclude_orgs_from_template(orgs):
    orgs = [org for org in orgs if not is_excluded(org['name'])]
    return orgs

def resource_url_fix(resource_url, same_domain):
    '''
        Returns the resource URL relative to the config file if the URL is on
        same domain.
    '''
    if same_domain == True:
        url_path = urlparse(resource_url).path
        return config.get('ckan.site_url') + url_path
    else:
        return resource_url


class CustomTheme(SingletonPlugin, toolkit.DefaultDatasetForm):
    implements(IConfigurer)
    implements(ITemplateHelpers)
    implements(IActions)
    implements(IPackageController, inherit=True)

    def before_search(self, search_params):
        return search_params

    def after_search(self, search_results, search_params):
        if (search_results['search_facets'].has_key('organization')):
            organizations = search_results['search_facets']['organization']['items']
            new_orgs = [org for org in organizations if not is_excluded(org['name'])]
            search_results['search_facets']['organization']['items'] = new_orgs
        return search_results

    def update_config(self, config):
        # Override the templates according to http://docs.ckan.org/en/latest/theming/templates.html
        toolkit.add_template_directory(config, "templates")
        toolkit.add_public_directory(config, "static")
        toolkit.add_resource('fanstatic', 'offgridtheme')

    def get_helpers(self):
        '''
        Registers the most_recent_datasets function as a template helper function
        '''
        return {
            'custom_theme_most_recent_datasets': most_recent_datasets,
            'custom_theme_resource_url_fix': resource_url_fix,
            'custom_theme_exclude_orgs': exclude_orgs_from_template
        }

    def get_actions(self):
        return {
            'organization_list': organization_list
        }

class OffgridPages(SingletonPlugin):
    """
        Add custom pages
    """
    implements(IConfigurer, inherit=True)
    implements(IRoutes, inherit=True)

    # IConfigurer
    def update_config(self, config_):
        toolkit.add_template_directory(config_, 'templates')

    def before_map(self, map):
        map.connect('apps', '/apps',
          controller='ckanext.offgridtheme.controller:AppsController',
          action='view')

        map.connect('terms', '/terms',
          controller='ckanext.offgridtheme.controller:TermsController',
          action='view')

        map.connect('privacy', '/privacy-policy',
          controller='ckanext.offgridtheme.controller:PrivacyController',
          action='view')

        # To add anoher page
        # map.connect('another', '/another',
        #   controller='ckanext.offgridtheme.controller:AnotherController',
        #   action='view')

        return map
