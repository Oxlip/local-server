"""
Simulates few plugz mote coap nodes.
"""

import logging
import string
import random
import time
import device_handler
import rest_client


class _PlugZMote(object):
    def __init__(self, device_id, serial, device_type):
        self.device_id = device_id
        self.device_type = device_type
        self._nodes = {
            '/dev/mfg': 'PlugZ',
            '/dev/mdl': self.device_type,
            '/dev/mdl/hw': 1.0,
            '/dev/mdl/sw': 1.0,
            '/dev/ser': serial
        }
        if self.device_type == 'uSwitch':
            for i in range(4):
                self._nodes['/pwr/{0}/w'.format(i)] = 0
                self._nodes['/pwr/{0}/kwh'.format(i)] = 0
                self._nodes['/pwr/{0}/rel'.format(i)] = 0
                self._nodes['/pwr/{0}/dim'.format(i)] = 100
        elif self.device_type == 'uPlug':
            self._nodes['/pwr/0/w'] = 0
            self._nodes['/pwr/0/kwh'] = 0
            self._nodes['/pwr/0/rel'] = 0
            self._nodes['/pwr/0/dim'] = 100
        elif self.device_type == 'uSense':
            self._nodes['/sen/temp'] = 30
            self._nodes['/sen/hum'] = 87
            self._nodes['/sen/lig'] = 78
            self._nodes['/sen/mot'] = 0


# simulated motes - key is the serial
_motes = {}


def _random_serial(size=10):
    """
    Helper function to generates a serial number.

    :param size: Max length of the serial number.
    :return: A random serial number composed of A-Z and 0-9
    """
    chars = string.ascii_uppercase + string.digits
    return 'SIM-' + (''.join(random.choice(chars) for _ in range(size)))


def initialize(rest_client, username='samueldotj', create_count=0):
    """
    Initialize plugz mote for simulation

    :param rest_client: REST client to use to communicate with the server.
    :param username: Profile id
    :param create_count: Number of motes to create
    :return: None
    """

    global _motes

    #create devices if needed.
    for i in range(create_count):
        serial = _random_serial()
        device_type = random.choice(['uSwitch', 'uPlug', 'uSense'])
        status, result = rest_client.register_device(username=username, serial_no=serial,
                                                     device_type=device_type, device_name=serial)
        if not status:
            logging.error('Registering sim mote failed')
            continue
        device_id = result['id']

    # load devcies by querying cloud server
    devices = rest_client.get_devices()
    for device in devices:
        device_id = device['id']
        device_type = device['type']
        _motes[device_id] = _PlugZMote(device_id=device_id, serial=None, device_type=device_type)


def get_device_list():
    """
    Returns list of devices being simulated.
    :return: List of device unique id.
    """
    global _motes
    return _motes.keys()


def set_device_value(device_id, node, value):
    global _motes
    if node in _motes[device_id]:
        _motes[device_id][node] = value
        logging.info('MOTE[{0}]:{1} -> {2}'.format(device_id, node, value))
    return


def get_device_value(device_id, node):
    global _motes
    return _motes[device_id][node]


def simulation_loop():
    """ The main simulation loop where device events are generated.
    """
    global _motes
    total_motes = len(_motes.keys())
    while True:
        # Randomly select few devices for generating the event
        select_count = random.choice(range(total_motes))
        for i in range(select_count):
            device_id = random.choice(_motes.keys())
            value = random.choice(range(100))
            time_range = random.choice(range(100))
            device_handler.handle_device_update(device_id, value, time_range)

        # Sleep with random interval
        time.sleep(random.choice(range(total_motes * 3)))
