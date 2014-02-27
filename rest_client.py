"""
REST client to access the remote server. Provides APIs to access remote server.
 This class will be used by the database class to sync the local db and remote server db.
"""

import requests

REST_SERVER_BASE = 'http://162.243.204.9/backend/api/v1/'


class RestClient:
    def __init__(self, hub_id):
        self.hub_id = hub_id
        self.channel_id = None

    def connect(self):
        """
        Makes connection to the server and reterives the channel id for notification.
        """
        url = '{base}/hub/{hub_id}/connect'.format(base=REST_SERVER_BASE, hub_id=self.hub_id)
        r = requests.get(url)
        json_result = r.json()
        #todo parse the JSON and get the channel id

        return self.channel_id

    def get_devices(self, full_refresh=False):
        """
        Makes REST call to server to fetch the device list associated with the user.
        """
        url = '{base}/hub/{hub_id}/'.format(base=REST_SERVER_BASE, hub_id=self.hub_id)
        r = requests.get(url)
        json_result = r.json()
        #todo parse the JSON and return list of devices
        return []

