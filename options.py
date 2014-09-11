from rest_client import RestClient
import gevent


options = {}

def get_hub_identity():
    """
    Reads IDPROM and returns hub identifier
    """
    # TODO - implement reading from beaglebone IDPROM
    # For now this is a test data (same as backend/models/ExampleData.SQL)
    return '123234', 'AUTH_KEY IS EMPTY'

def set_hub(hub):
    options['hub'] = hub

def get_hub(wait = False):
    if 'hub' not in options:
        if not wait:
            return None
        client = RestClient()
        hub_identity, authentication_key = get_hub_identity()
        hub = None
        while hub is None and 'hub' not in options:
            client.hub_connect(hub_identity, authentication_key)
            gevent.sleep(5)
    return options['hub']
