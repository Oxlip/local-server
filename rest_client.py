"""
REST client to access the remote server. Provides APIs to access remote server.
 This class will be used by the database class to sync the local db and remote server db.
"""

import requests
from datetime import datetime
import uhub_exceptions
import logging

REST_SERVER_BASE_IP = '162.243.204.9'
#REST_SERVER_BASE_IP = '192.168.1.74:8000'

class RestReq(object):

    def __init__(self, base, parent, action):
        self.base   = base
        self.parent = parent
        self.action = action


    def url_format(self, id):
        url = '{base}/{parent}'.format(base = self.base, parent = self.parent)
        if id != '':
           url = '{url}/{added}'.format(url = url, added = id)
        if self.action != '':
           url = '{url}/{added}'.format(url = url, added = self.action)

        return url


    def get(self, id = ''):
        url = self.url_format(id)
        req = requests.get(url)
        http_code = req.status_code
        try:
            result = req.json()
        except:
            logging.error('Receive non-json result from: {url}'.format(url=url))
            result = []

        logging.debug('Connect to url:{url} http_code:{status}\n{msg}'.format(
           url = url,
           status = http_code,
           msg = result))

        return http_code, result


    def post(self, id = '', post = {}, headers = {}):
        url = self.url_format(id)
        logging.debug('Forge url [{url}]'.format(url=url))
        logging.debug('Headers:\n{headers}'.format(headers=headers))
        req = requests.post(url, headers=headers, data=post)
        http_code = req.status_code
        try:
            result = req.json()
        except:
            logging.error('Receive non-json result from: {url}'.format(url=url))
            result = []

        logging.debug('Connect to url:{url} http_code:{status}\n{msg}'.format(
           url = url,
           status = http_code,
           msg = result))

        return http_code, result



class RestClient(object):

    _api_url = 'http://{ip}/api/v1'.format(ip = REST_SERVER_BASE_IP)

    def __getattr__(self, name):
        try:
            _first = name.index('_')
            type = name[:_first]
            _first = _first + 1

            if name.count('_') > 1:
                _second = name.index('_', _first)
                parent = name[_first:_second]
                action = name[_second + 1:]
            else:
                parent = name[_first:]
                action = ''

            return getattr(RestReq(self._api_url, parent, action), type)
        except:
            raise Exception("RestClient don't have {0} as attribute".format(name))

    def __init__(self):
        pass


    def hub_connect(self, hub_identification, authentication_key):
        """
        Makes connection to the server and retrieves the hub information
        (hub_id, channel id for notification).
        """

        headers = {'http_auth_key': authentication_key}
        status_code, hub = self.post_hub_connect(id = hub_identification,
                                                 headers = headers)
        if status_code != requests.codes.ok:
            # TODO - retry before giving up
            logging.error(
                'Connecting uHub to cloud failed. Status code - {0}'.format(status_code)
            )
            return None
        hub['identification'] = hub_identification
        return hub

    def get_devices(self, hub_id, full_refresh=False):
        """
        Makes REST call to server to fetch the device list associated with the user.
        """

        http_status, result = self.get_hub_devices(hub_id)
        if http_status == requests.codes.ok and 'devices' in result:
           return result['devices']
        return []

    def send_device_value(self, device_id, time_range, source, value):
        """
        Makes REST call to server to update a change in a device's value
        """
        params = {
            'device_id': device_id,
            'timestamp': datetime.now(),
            'time_range': time_range,
            'source': source,
            'value': value
        }
        http_status, result = self.post_device_activity(device_id, post = params)
        return http_status == requests.codes.ok


    def get_user_info(self, username):
        http_status, result = self.get_user(username)
        return http_status == requests.codes.ok, result


    def register_device(self, username, serial_no, device_type, device_name, hub_id):
        """
        Makes REST call to server to register a device with given username.
        Note - this should be used only for simulation.
        """
        params = {
            'serial_no': serial_no,
            'device_type': device_type,
            'device_name': device_name,
            'hub_identification': hub_id
        }
        http_status, result = self.post_user_register_device(username, post = params)

        return http_status == requests.codes.ok, result
