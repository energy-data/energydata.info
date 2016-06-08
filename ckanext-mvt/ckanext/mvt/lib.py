from subprocess import call

import os
import ckanapi
import requests
import uuid
import shutil

TEMPDIR = '/tmp'

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

def generate_mvt(filepath, mvtfile):
    returncode = call([
        'tippecanoe', '-q', '-o', mvtfile, filepath
    ])
    if returncode != 0:
       raise BadResourceFileException("{0} could not be converted to mvt".format(filepath))

    else:
        return returncode

def upload_to_s3(filepath, s3id, s3config):
    tileurl = "{0}/tiles/{1}/{{z}}/{{x}}/{{y}}.pbf".format(s3config['bucket'], s3id)
    aws_env = os.environ.copy()
    aws_env['AWS_ACCESS_KEY_ID'] = s3config['access_key']
    aws_env['AWS_SECRET_ACCESS_KEY'] = s3config['secret_key']

    returncode = call([
        'mapbox-tile-copy', filepath, tileurl
    ], env=aws_env)

    if returncode != 0:
        raise S3Exception("{0} could not be uploaded to s3")

    else:
        return returncode

def process(ckan, resource_id, s3config):
    if not os.path.isdir(TEMPDIR):
        os.makedirs(TEMPDIR)

    try:
        resource = ckan.action.resource_show(id=resource_id)
        print resource
        file_format = resource['format'].upper()

        if file_format == 'GEOJSON':
            file = download_file(resource['url'], ckan.apikey)
            filepath = os.path.join(TEMPDIR, file)
            mvtfile = os.path.join(TEMPDIR, '{0}.mbtiles'.format(filepath))
            returncode =  generate_mvt(filepath, mvtfile)
            returncode =  upload_to_s3(mvtfile, resource_id, s3config)

            print "{0} processed from celery".format(resource_id)
            print "return code {0}".format(returncode)
    except (S3Exception, BadResourceFileException) as e:
        print e
        return

