import logging
import ckan.lib.base as base
import ckan.plugins.toolkit as toolkit
import ckan.model as model

from ckan.common import response
import json
import base64

log = logging.getLogger(__name__)

def _error_response(status_code, msg):
    response.status = status_code
    return msg

def _get_credentials(auth_header):
    authmeth, token = auth_header.split(' ', 1)
    if authmeth.lower() == 'basic':
        try:
            decoded_token = token.strip().decode('base64')
        except binascii.Error:
            return None
        try:
            login, password = decoded_token.split(':', 1)
        except ValueError:
            return None
        return {'login': login, 'password': password}
    return None

def _get_key(credentials):
    user = model.User.get(credentials['login'])
    if user == None:
        return None
    if user.validate_password(credentials['password']):
        return user.apikey
    else:
        return None

class AuthKeyController(base.BaseController):

    def exchange(self):
        auth_header = toolkit.request.headers.get('Authorization')
        if auth_header == None:
            return _error_response(403, 'Unauthorized')

        credentials = _get_credentials(auth_header)
        if credentials == None:
            return _error_response(500, 'Could not parse request')

        apikey = _get_key(credentials)
        if apikey == None:
            return _error_response(403, 'Unauthorized')

        response.headers['Content-Type'] = 'application/json'
        return json.dumps({'user': credentials['login'], 'apikey': apikey})

