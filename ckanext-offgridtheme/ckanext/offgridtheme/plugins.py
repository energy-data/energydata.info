from ckan.plugins import toolkit, IConfigurer, SingletonPlugin, IRoutes, implements

class CustomTheme(SingletonPlugin):
    implements(IConfigurer)

    def update_config(self, config):
        toolkit.add_template_directory(config, "templates")
        toolkit.add_public_directory(config, "static")
        toolkit.add_resource('fanstatic', 'offgridtheme')

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
