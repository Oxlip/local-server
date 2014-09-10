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

    def post(self, id = '', post = {}, headers = {}):
        url = '{base}/{parent}/{id}/{action}'.format(base = self.base,
                                                     parent = self.parent,
                                                     id = id,
                                                     action = self.action)
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



class RestClient:

    _api_url = 'http://{ip}/api/v1'.format(ip = REST_SERVER_BASE_IP)

    def __getattr__(self, name):
       names = name.split('_')
       return getattr(RestReq(self._api_url, names[1], names[2]), names[0])

    def __init__(self, hub_identification, authentication_key):
        """
        Makes connection to the server and retrieves the hub information
        (hub_id, channel id for notification).
        """

        headers = {'http_auth_key': authentication_key}
        status_code, hub = self.post_hub_connect(id = hub_identification,
                                                 headers = headers)
        if status_code != requests.codes.ok:
            # TODO - retry before giving up
            raise uhub_exceptions.ConnectFailedError('Connecting uHub to cloud failed. Status code - {0}'.format(status_code))

        self.hub_id = hub['id']
        self.channel_id = hub['channel']
        self.hub_identification = hub_identification

    def get_devices(self, full_refresh=False):
        """
        Makes REST call to server to fetch the device list associated with the user.
        """
        url = '{base}/hub/{identification}/devices'.format(base=REST_SERVER_BASE, identification=self.hub_identification)
        r = requests.get(url)
        if r.status_code != requests.codes.ok:
            logging.error('Failed to fetch device list from cloud server {0}'.format(r.status_code))
            return []

        return r.json()['devices']

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
        url = '{base}/device/{device_id}/activity'.format(base=REST_SERVER_BASE, device_id=device_id)
        r = requests.post(url, data=params)

        return r.status_code == requests.codes.ok

    def register_device(self, username, serial_no, device_type, device_name):
        """
        Makes REST call to server to register a device with given username.
        Note - this should be used only for simulation.
        """
        params = {
            'serial_no': serial_no,
            'device_type': device_type,
            'device_name': device_name,
            'hub_identification': self.hub_identification
        }
        url = '{base}/user/{username}/register_device'.format(base=REST_SERVER_BASE, username=username)
        r = requests.post(url, data=params)

        return r.status_code == requests.codes.ok, r.json()
