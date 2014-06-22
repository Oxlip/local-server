"""
REST client to access the remote server. Provides APIs to access remote server.
 This class will be used by the database class to sync the local db and remote server db.
"""

import requests
from datetime import datetime
import plugz_exceptions

REST_SERVER_BASE = 'http://162.243.204.9/api/v1'
#REST_SERVER_BASE = 'http://127.0.0.1:8000/api/v1'


class RestClient:
    def __init__(self, hub_identification, authentication_key):
        """
        Makes connection to the server and retrieves the hub information (hub_id, channel id for notification).
        """
        url = '{base}/hub/{identification}/connect'.format(base=REST_SERVER_BASE, identification=hub_identification)
        r = requests.post(url, headers={'http_auth_key': authentication_key})
        if r.status_code != requests.codes.ok:
            # TODO - retry before giving up
            raise plugz_exceptions.ConnectFailedError('REST connection failed {0}'.format(r.status_code))

        hub = r.json()
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
            return None

        return r.json()['devices']

    def send_device_status(self, device_id, time_range, value):
        """
        Makes REST call to server to update a change in a device's value
        """
        params = {
            'device_id': device_id,
            'timestamp': datetime.now(),
            'time_range': time_range,
            'value': value
        }
        url = '{base}/device/{device_id}/activity'.format(base=REST_SERVER_BASE, device_id=device_id)
        r = requests.post(url, data=params)

        return r.status_code == requests.codes.ok
