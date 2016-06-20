from subprocess import call

import os
import ckanapi
import requests
import uuid
import shutil
import hashlib
import json
import pickledb
import logging
import tempfile

from ckan.plugins import toolkit

log = logging.getLogger(__name__)

TEMPDIR = tempfile.mkdtemp(prefix='ckan')

NotFound = toolkit.ObjectNotFound

class BadResourceFileException(Exception):
    def __init__(self, extra_msg=None):
        self.extra_msg = extra_msg

    def __str__(self):
        return self.extra_msg

class S3Exception(Exception):
    def __init__(self, extra_msg=None):
        self.extra_msg = extra_msg

    def __str__(self):
        return self.extra_msg

class CKANAPIException(Exception):
    def __init__(self, extra_msg=None):
        self.extra_msg = extra_msg

    def __str__(self):
        return self.extra_msg

def download_file(url, apikey):
    tmpname = '{0}.geojson'.format(uuid.uuid1())
    response = requests.get(url, headers = {
        'Authorization': apikey
    }, stream = True)

    if response.status_code != 200:
        raise BadResourceFileException("{0} could not be downloaded".format(url))
    else:
        print "{0} was downloaded".format(url)

    with open(os.path.join(TEMPDIR, tmpname), 'wb') as out_file:
        shutil.copyfileobj(response.raw, out_file)

    return tmpname

def generate_mvt(filepath):
    mvtfile = os.path.join(TEMPDIR, '{0}.mbtiles'.format(filepath))
    returncode = call([
        'tippecanoe', '-l', 'data_layer', '-q', '-o', mvtfile, filepath
    ])
    if returncode != 0:
       raise BadResourceFileException("{0} could not be converted to mvt".format(filepath))

    else:
        return mvtfile

# From http://joelverhagen.com/blog/2011/02/md5-hash-of-file-in-python/
def _md5checksum(filepath):
    with open(filepath, 'rb') as fh:
        m = hashlib.md5()
        while True:
            data = fh.read(8192)
            if not data:
                break
            m.update(data)
    return m.hexdigest()

def upload_to_s3(filepath, s3id, s3config):
    revision = uuid.uuid1();
    tileurl = "{0}/tiles/{1}-{2}/{{z}}/{{x}}/{{y}}.pbf".format(
        s3config['bucket'],
        revision,
        s3id)
    aws_env = os.environ.copy()
    aws_env['AWS_ACCESS_KEY_ID'] = s3config['access_key']
    aws_env['AWS_SECRET_ACCESS_KEY'] = s3config['secret_key']

    returncode = call([
        'mapbox-tile-copy', filepath, tileurl
    ], env=aws_env)

    if returncode != 0:
        raise S3Exception("{0} could not be uploaded to s3".format(filepath))

    else:
        return tileurl

def _update_resource(resource, ckan):
    response = requests.post(
        ckan.address + '/api/action/resource_update',
        data = json.dumps(resource),
        headers = {
            'Content-Type': 'application/json',
            'Authorization': ckan.apikey
        }
    )
    if response.status_code not in (201, 200):
        raise CKANAPIException('CKAN response {0}'.format(response.status_code))
    else:
        log.info('{0} update successful'.format(resource['id']))

def _get_checksum_from_cache(resource_id):
   # Get from pickledb
    db = pickledb.load(os.path.join(TEMPDIR, 'checksums.db'), False)
    try:
        return db.get(resource_id)
    except KeyError:
        return None

def _set_checksum_in_cache(resource_id, checksum):
    db = pickledb.load(os.path.join(TEMPDIR, 'checksums.db'), True)
    db.set(resource_id, checksum)

def _get_s3url_from_cache(resource_id):
    db = pickledb.load(os.path.join(TEMPDIR, 's3urls.db'), False)
    try:
        return db.get(resource_id)
    except KeyError:
        return None

def _set_s3url_in_cache(resource_id, s3url):
    db = pickledb.load(os.path.join(TEMPDIR, 's3urls.db'), True)
    db.set(resource_id, s3url)

def process(ckan, resource_id, s3config):
    if not os.path.isdir(TEMPDIR):
        os.makedirs(TEMPDIR)

    try:
        resource = ckan.action.resource_show(id=resource_id)
        file_format = resource['format'].upper()

        if file_format == 'GEOJSON':
            # First download the file
            file = download_file(resource['url'], ckan.apikey)
            filepath = os.path.join(TEMPDIR, file)

            # Checksum the file contents and see if it matches the resource checksum
            checksum = _md5checksum(filepath)
            checksum_from_file = _get_checksum_from_cache(resource_id)

            # S3URL is either in the cache or nil
            s3url = _get_s3url_from_cache(resource_id)

            if checksum != checksum_from_file:
                log.info("old: {0} != new: {1}".format(checksum_from_file, checksum))
                # Update the file
                _set_checksum_in_cache(resource_id, checksum)

                mvtfile = generate_mvt(filepath)
                s3url =  upload_to_s3(mvtfile, resource_id, s3config)
                _set_s3url_in_cache(resource_id, s3url)

            else:
                log.info("{0}".format("content hasn't changed"))

            # Update the s3url
            resource['tilejson'] = s3url
            _update_resource(resource, ckan)
            new_resource = ckan.action.resource_show(id=resource_id)
            log.info(new_resource)

    except (S3Exception, BadResourceFileException, NotFound, CKANAPIException) as e:
        print e
        return

