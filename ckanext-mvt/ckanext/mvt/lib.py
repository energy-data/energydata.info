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
import boto3
import re
import sqlite3

from ckan.plugins import toolkit

log = logging.getLogger(__name__)

logging.getLogger('boto3').setLevel(logging.WARNING)
logging.getLogger('botocore').setLevel(logging.WARNING)
logging.getLogger('nose').setLevel(logging.WARNING)

NotFound = toolkit.ObjectNotFound

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

class CacheHandler:
    def __init__(self, tempdir):
        self.checksums = os.path.join(tempdir, 'checksums.db')
        self.s3urls = os.path.join(tempdir, 's3urls.db')

    def get_checksum(self, resource_id):
        db = pickledb.load(self.checksums, False)
        try:
            return db.get(resource_id)
        except KeyError:
            return None

    def set_checksum(self, resource_id, checksum):
        db = pickledb.load(self.checksums, True)
        db.set(resource_id, checksum)

    def get_s3url(self, resource_id):
        db = pickledb.load(self.s3urls, False)
        try:
            return db.get(resource_id)
        except KeyError:
            return None

    def set_s3url(self, resource_id, s3url):
        db = pickledb.load(self.s3urls, True)
        db.set(resource_id, s3url)

    def get_s3url_keys(self):
        db = pickledb.load(self.s3urls, False)
        return db.getall()

    def delete(self, resource_id):
        db = pickledb.load(self.s3urls, True)
        db.rem(resource_id)
        db = pickledb.load(self.checksums, True)
        db.rem(resource_id)

class TileProcessor:
    """
    Celery Task Processor for GeoJSON resources
    * Creates/Updates tiles for current resources
    * Deletes tiles for deleted resource
    """
    def __init__(self, ckan, s3config, tempdir):
       self.ckan = ckan
       self.s3config = s3config
       self.tempdir = tempdir
       self.cache = CacheHandler(tempdir)
       print "from celery temdpir is {}".format(tempdir)
       if not os.path.isdir(tempdir):
           os.makedirs(tempdir)

    def _download_file(self, url):
        tmpname = '{0}.geojson'.format(uuid.uuid4())
        response = requests.get(url, headers = {
            'Authorization': self.ckan.apikey
        }, stream = True)

        if response.status_code != 200:
            raise BadResourceFileException("{0} could not be downloaded".format(url))
        else:
            print "{0} was downloaded".format(url)

        with open(os.path.join(self.tempdir, tmpname), 'wb') as out_file:
            shutil.copyfileobj(response.raw, out_file)

        return tmpname

    def _generate_mvt(self, filepath):
        """
        Uses tippecanoe to generate vector tiles from a GeoJSON file
        """
        mvtfile = '{0}.mbtiles'.format(filepath)
        returncode = call([
            # 12 zoom levels ought to be enough for anybody
            'tippecanoe', '-r', '1.5', '-z', '12', '-l', 'data_layer', '-q', '-o', mvtfile, filepath
        ])
        if returncode != 0:
            raise BadResourceFileException("{0} could not be converted to mvt".format(filepath))

        else:
            return mvtfile

    def _update_resource(self, resource):
        """
        Updates a resource's metadata using the CKAN API
        """
        response = requests.post(
            self.ckan.address + '/api/action/resource_update',
            data = json.dumps(resource),
            headers = {
                'Content-Type': 'application/json',
                'Authorization': self.ckan.apikey
            }
        )
        if response.status_code not in (201, 200):
            raise CKANAPIException('CKAN response {0}'.format(response.status_code))
        else:
            log.info('{0} update successful'.format(resource['id']))

    def _upload_to_s3(self, filepath, extent, resource_id):
        """
        Upload the generated tiles from _generate_mvt to s3
        This function also stores the url in the cache file
        """
        s3 = boto3.resource(
            's3',
            aws_access_key_id= self.s3config['access_key'],
            aws_secret_access_key= self.s3config['secret_key']
        )

        # Upload tiles
        revision = uuid.uuid4();
        bucket = self.s3config['bucket']
        prefix = "tiles/{0}-{1}".format(
            resource_id,
            revision
            )

        tileurl = "s3://{0}/{1}/{{z}}/{{x}}/{{y}}.pbf".format(bucket, prefix)
        httptileurl = "https://{0}.s3.amazonaws.com/{1}/{{z}}/{{x}}/{{y}}.pbf".format(bucket, prefix)

        aws_env = os.environ.copy()
        aws_env['AWS_ACCESS_KEY_ID'] = self.s3config['access_key']
        aws_env['AWS_SECRET_ACCESS_KEY'] = self.s3config['secret_key']

        returncode = call([
            'mapbox-tile-copy', filepath, tileurl
        ], env=aws_env)

        # Upload tilejson
        tilejson = {
            "tilejson": "2.1.0",
            "format": "pbf",
            "tiles": [httptileurl],
            "vector_layers": [{"id": "data_layer"}]
        }
        bounds = extent.split(',')
        if len(bounds) == 4:
            tilejson['bounds'] = [float(x) for x in bounds]
        log.info(json.dumps(tilejson))
        key = s3.Object(bucket_name=bucket, key='{0}/data.tilejson'.format(prefix))
        key.put(Body=json.dumps(tilejson))

        if returncode != 0:
            raise S3Exception("{0} could not be uploaded to s3".format(filepath))

        else:
            return "https://{0}.s3.amazonaws.com/{1}/data.tilejson".format(bucket, prefix)

    def _delete_old_tiles(self, tilejson_url):
        matches = re.search('(.*)/tiles/(.*)/data.tilejson', tilejson_url)
        if matches and len(matches.groups()) == 2:
            old_resource_url = matches.group(2) #resoure_id-revision
            s3 = boto3.resource(
                's3',
                aws_access_key_id= self.s3config['access_key'],
                aws_secret_access_key= self.s3config['secret_key']
            )
            bucket = s3.Bucket(self.s3config['bucket'])
            bucket.objects.filter(Prefix='tiles/{}'.format(old_resource_url)).delete()
        else:
            log.info("Could not match {}".format(tilejson_url))

    def _get_extent(self, mvtfile):
        conn = sqlite3.connect(mvtfile)
        cursor = conn.cursor()
        cursor.execute('''
        select value from METADATA where name='bounds';
        ''')
        row = cursor.fetchone()
        return row[0]

    def update(self, resource_id):
        """
        Celery Task to create vector tiles for a new resource,
         or update the tiles if a resource's content changes.
        To detect content changes, this function stores a checksum for each
        resource in a temporary cache file.
        """
        try:
            resource = self.ckan.action.resource_show(id=resource_id)
            file_format = resource['format'].upper()

            if file_format == 'GEOJSON':
                # First download the file
                file = self._download_file(resource['url'])
                filepath = os.path.join(self.tempdir, file)

                # Checksum the file contents and see if it matches the resource checksum
                checksum = _md5checksum(filepath)
                checksum_from_file = self.cache.get_checksum(resource_id)

                if checksum != checksum_from_file:
                    # If an s3url exists, we want to delete the tiles there and
                    # push at another url
                    old_url = self.cache.get_s3url(resource_id)

                    log.info("old: {0} != new: {1}".format(checksum_from_file, checksum))

                    # Generate tiles
                    mvtfile = self._generate_mvt(filepath)
                    extent = self._get_extent(mvtfile)
                    s3url = self._upload_to_s3(mvtfile, extent, resource_id)
                    self.cache.set_s3url(resource_id, s3url)

                    # Update the s3url
                    resource['tilejson'] = s3url
                    self._update_resource(resource)

                    # Update the checksum if everything works
                    self.cache.set_checksum(resource_id, checksum)

                    # Delete the local vector tiles
                    os.remove(mvtfile)

                    # Delete the old tiles
                    if old_url:
                        log.info("Deleting {0}".format(old_url))
                        self._delete_old_tiles(old_url)

                else:
                    log.info("content hasn't changed")

                # Delete the downloaded resource
                os.remove(filepath)


        except (S3Exception, BadResourceFileException, NotFound, CKANAPIException) as e:
            print e
            return

    def delete(self, resource_id):
        """
        Deletes s3 tiles for a resource scheduled for deletion. This function
        deletes the entry in the cache file.
        """
        try:
            # Check if the URL is in the cache
            s3url = self.cache.get_s3url(resource_id)
            if s3url:
                log.info("Deleting {0}".format(s3url))
                self._delete_old_tiles(s3url)
                self.cache.delete(resource_id)

        except (S3Exception, BadResourceFileException, NotFound, CKANAPIException) as e:
            print e
            return
