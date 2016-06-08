import ckan.plugins as plugins
import ckan.plugins.toolkit as toolkit
import ckan.model as model
from ckan.lib.celery_app import celery

import pylons.config as config
import pylons
import uuid
import ckanapi

class MvtPlugin(plugins.SingletonPlugin):
    plugins.implements(plugins.IDomainObjectModification, inherit=True)
    plugins.implements(plugins.IConfigurer)


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
