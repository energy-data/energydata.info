from ckan.lib.celery_app import celery
from requests import get
from lib import TileProcessor

import ckanapi

@celery.task(name='mvt.process_resource')
def process_resource(resource_id, site_url, apikey, s3config, tempdir, action = 'update'):
    ckan = ckanapi.RemoteCKAN(site_url, apikey=apikey)
    tileprocessor = TileProcessor(ckan, s3config, tempdir)
    print("processing resource {0}".format(resource_id))
    if action == 'create' or action == 'update':
        tileprocessor.update(resource_id)
    elif action == 'delete':
        tileprocessor.delete(resource_id)
