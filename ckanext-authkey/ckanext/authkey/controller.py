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

def _get_credentials(body):
    login, password = body.split('&', 1)
    if login and password:
        login_k, login_v = login.split('=', 1)
        password_k, password_v = password.split('=', 1)
        if login_v and password_v and login_k == 'username' and password_k == 'password':
            return {'login': login_v, 'password': password_v}
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
        if toolkit.request.method == 'POST':
            credentials = _get_credentials(toolkit.request.body)
            if credentials == None:
                return _error_response(500, 'Could not parse request')
            apikey = _get_key(credentials)
            if apikey == None:
                return _error_response(403, 'Unauthorized')

            response.headers['Content-Type'] = 'application/json'
            return json.dumps({'user': credentials['login'], 'apikey': apikey})

        else:
            return _error_response(403, 'Unauthorized')



