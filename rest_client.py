"""
REST client to access the remote server. Provides APIs to access remote server.
 This class will be used by the database class to sync the local db and remote server db.
"""

import requests
import plugz_exceptions

#REST_SERVER_BASE = 'http://162.243.204.9/backend/api/v1'
REST_SERVER_BASE = 'http://127.0.0.1:8000/backend/api/v1'


class RestClient:
    def __init__(self, hub_identification):
        """
        Makes connection to the server and retrieves the hub information (hub_id, channel id for notification).
        """
        url = '{base}/hub/{identification}'.format(base=REST_SERVER_BASE, identification=hub_identification)
        r = requests.get(url)
        if r.status_code != requests.codes.ok:
            # TODO - retry before giving up
            raise plugz_exceptions.ConnectFailedError('REST connection failed {0}'.format(r.status_code))

        hub = r.json()
        self.hub_id = hub['id']
        self.channel_id = hub['channel_id']
        self.name = hub['name']
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

