import ckan.plugins as plugins
import ckan.plugins.toolkit as toolkit
import ckan.model as model
from ckan.lib.celery_app import celery

import pylons.config as config
import pylons
import uuid
import ckanapi

class MvtPlugin(plugins.SingletonPlugin, toolkit.DefaultDatasetForm):
    plugins.implements(plugins.IDomainObjectModification, inherit=True)
    plugins.implements(plugins.IDatasetForm)
    plugins.implements(plugins.IConfigurer)

    def _modify_pkg_schema(self, schema):
        schema['resources'].update({
            's3url': [
                toolkit.get_validator('ignore_missing'),
            ],
            'checksum': [
                toolkit.get_validator('ignore_missing'),
            ],
        })
        return schema

    def _show_pkg_schema(self, schema):
        schema['resources'].update({
            's3url': [
                toolkit.get_validator('ignore_missing'),
            ],
            'checksum': [
                toolkit.get_validator('ignore_missing'),
            ],
        })
        return schema

    def is_fallback(self):
        # Return True to register this plugin as the default handler for
        # package types not handled by any other IDatasetForm plugin.
        return True

    def package_types(self):
        # This plugin doesn't handle any special package types, it just
        # registers itself as the default (above).
        return []

    def create_package_schema(self):
        schema = super(MvtPlugin, self).create_package_schema()
        schema = self._modify_pkg_schema(schema)
        return schema

    def update_package_schema(self):
        schema = super(MvtPlugin, self).update_package_schema()
        schema = self._modify_pkg_schema(schema)
        return schema

    def show_package_schema(self):
        schema = super(MvtPlugin, self).show_package_schema()
        schema = self._show_pkg_schema(schema)
        return schema

    # IConfigurer
    def update_config(self, config_):
        toolkit.add_template_directory(config_, 'templates')
        toolkit.add_public_directory(config_, 'public')
        toolkit.add_resource('fanstatic', 'mvt')

    # IDomainObjectModification
    def notify(self, entity, operation = None):
        # Check if we have a resource
        if isinstance(entity, model.Resource):

            resource_id = entity.id
            if (operation == model.domain_object.DomainObjectOperation.changed or
                operation == model.domain_object.DomainObjectOperation.new):
                site_url = config.get('ckan.site_url', 'http://localhost/')
                apikey = model.User.get('default').apikey
                s3config = {
                    'bucket': config.get('ckanext.mvt.s3.bucket'),
                    'access_key': config.get('ckanext.mvt.s3.access_key'),
                    'secret_key': config.get('ckanext.mvt.s3.secret_key')
                }

                celery.send_task(
                    'mvt.process_resource',
                    args=[resource_id, site_url, apikey, s3config],
                    task_id='{}-{}'.format(str(uuid.uuid4()), operation)
                )
