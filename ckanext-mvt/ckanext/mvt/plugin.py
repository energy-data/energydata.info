import ckan.plugins as plugins
import ckan.plugins.toolkit as toolkit
import ckan.model as model
from ckan.lib.celery_app import celery
import ckan.lib.datapreview as datapreview

import pylons.config as config
import pylons
import uuid
import ckanapi
import tempfile
import os
import logging
import lib

log = logging.getLogger(__name__)

def _celery_task(resource_id, action, tempdir):
    site_url = config.get('ckan.site_url', 'http://localhost/')
    apikey = model.User.get('default').apikey
    s3config = {
        'bucket': config.get('ckanext.mvt.s3.bucket'),
        'access_key': config.get('ckanext.mvt.s3.access_key'),
        'secret_key': config.get('ckanext.mvt.s3.secret_key'),
    }

    if action == 'create' or action == 'update' or action == 'delete':
        celery.send_task(
            'mvt.process_resource',
            args=[
                resource_id,
                site_url,
                apikey,
                s3config,
                tempdir,
                action
            ],
            task_id='{}-{}'.format(str(uuid.uuid4()), action)
        )


class MvtPlugin(plugins.SingletonPlugin, toolkit.DefaultDatasetForm):
    plugins.implements(plugins.IDatasetForm)
    plugins.implements(plugins.IResourceController, inherit=True)

    TEMPDIR = os.path.join(os.path.dirname(__file__), '..', 'tmp')

    #IDatasetForm
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


    # IResourceController
    def after_create(self, context, resource):
        _celery_task(resource['id'], 'create', MvtPlugin.TEMPDIR)

    def after_update(self, context, resource):
        _celery_task(resource['id'], 'update', MvtPlugin.TEMPDIR)

    def before_delete(self, context, resource, resources):
        _celery_task(resource['id'], 'delete', MvtPlugin.TEMPDIR)

    def before_show(self, data_dict):
        cache = lib.CacheHandler(MvtPlugin.TEMPDIR)
        s3url = cache.get_s3url(data_dict.get('id'))
        data_dict['tilejson'] = s3url
        return data_dict

class MvtViewPlugin(plugins.SingletonPlugin):

    plugins.implements(plugins.IConfigurer, inherit=True)
    plugins.implements(plugins.IResourceView, inherit=True)

    # IConfigurer

    def update_config(self, config_):
        toolkit.add_template_directory(config_, 'templates')

    # IResourceView

    def info(self):
        return {
            'name': 'mvt_view',
            'title': 'Map View',
            'icon': 'globe',
            'iframed': True,
            'always_available': False
        }

    def setup_template_variables(self, context, data_dict):
        return {
            'tilejson': data_dict['resource'].get('tilejson', '')
        }


    def can_view(self, data_dict):
        return data_dict['resource'].get('format', '').lower() == 'geojson'

    def view_template(self, context, data_dict):
        return 'mvtview.html'

    def after_update(self, context, data_dict):
        self.add_default_views(context, data_dict)

    def after_create(self, context, data_dict):
        self.add_default_views(context, data_dict)
