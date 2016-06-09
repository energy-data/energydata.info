import ckan.plugins as plugins
import ckan.plugins.toolkit as toolkit

import logging
log = logging.getLogger(__name__)

class AuthkeyPlugin(plugins.SingletonPlugin):
    plugins.implements(plugins.IRoutes, inherit=True)

    # IRoutes
    def before_map(self, map):
        map.connect(
            'authkey_exchange',
            '/authkey',
            controller='ckanext.authkey.controller:AuthKeyController',
            action='exchange')
        return map
