from ckan.plugins import toolkit, IConfigurer, ITemplateHelpers, SingletonPlugin, IRoutes, implements
from urlparse import urlparse
import pylons.config as config

def most_recent_datasets():
    ''' Returns three most recently modified datasets'''
    datasets = toolkit.get_action('current_package_list_with_resources')(data_dict={
        'limit': 3
    })
    return datasets

def resource_url_fix(resource_url):
    '''Returns the resource URL relative to the config file'''
    url_path = urlparse(resource_url).path
    return config.get('ckan.site_url') + url_path

class CustomTheme(SingletonPlugin):
    implements(IConfigurer)
    implements(ITemplateHelpers)

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
