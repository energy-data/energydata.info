from ckan.lib.celery_app import celery
from requests import get
from lib import process

import ckanapi

@celery.task(name='mvt.process_resource')
def process_resource(resource_id, site_url, apikey, s3config):
    ckan = ckanapi.RemoteCKAN(site_url, apikey=apikey)
    print("processing resource {0}".format(resource_id))
    process(ckan, resource_id, s3config)
