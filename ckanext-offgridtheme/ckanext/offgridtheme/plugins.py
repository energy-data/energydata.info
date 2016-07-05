from ckan.plugins import toolkit, IConfigurer, ITemplateHelpers, SingletonPlugin, IRoutes, implements

def most_recent_datasets():
    ''' Returns three most recently modified datasets'''
    datasets = toolkit.get_action('current_package_list_with_resources')(data_dict={
        'limit': 3
    })
    return datasets

class CustomTheme(SingletonPlugin):
    implements(IConfigurer)
    implements(ITemplateHelpers)

    def update_config(self, config):
        toolkit.add_template_directory(config, "templates")
        toolkit.add_public_directory(config, "static")
        toolkit.add_resource('fanstatic', 'offgridtheme')

    def get_helpers(self):
        '''
        Registers the most_recent_datasets function as a template helper function
        '''
        return {'custom_theme_most_recent_datasets': most_recent_datasets}

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
        map.connect('tools', '/tools',
          controller='ckanext.offgridtheme.controller:ToolsController',
          action='view')

        # To add anoher page
        # map.connect('another', '/another',
        #   controller='ckanext.offgridtheme.controller:AnotherController',
        #   action='view')

        return map
