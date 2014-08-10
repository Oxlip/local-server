"""
Simulates few motes.
"""

import logging
import string
import random
import time
import devices
from datetime import datetime


class _Mote(object):
    def __init__(self, device_id, serial, device_type):
        self.device_id = device_id
        self.device_type = device_type
        self.serial = serial
        if self.device_type in ['uSwitch', 'uPlug']:
            self._max_load = random.choice(range(10, 100))
            self._current_sensor = 0
            self._cs_time = datetime.now()
            self._button_state = 0
        elif self.device_type == 'uSense':
            self._temp_sensor = 30
            self._humidity_sensor = 80
            self._light_sensor = 70
            self._motion_sensor = 0
            self._gas_sensor = 0

    def set_value(self, value):
        if self.device_type not in ['uSwitch', 'uPlug']:
            return
        self._button_state = value

    def get_value(self, source):
        if self.device_type in ['uSwitch', 'uPlug'] and source == 'C':
            return self._current_sensor
        elif self.device_type == 'uSense':
            if source == 'T':
                return self._temp_sensor
            elif source == 'H':
                return self._humidity_sensor
            elif source == 'M':
                return self._motion_sensor
            elif source == 'L':
                return self._light_sensor
            elif source == 'G':
                return self._gas_sensor

    def simulate(self):
        """ Simulates the given mote.
        """
        if self.device_type in ['uSwitch', 'uPlug']:
            devices.handle_device_update(self.device_id, source='B', value=self._button_state, time_range=1)
            total_load = self._max_load / 100 * self._button_state
            devices.handle_device_update(self.device_id, source='C', value=total_load, time_range=1)
        elif self.device_type == 'uSense':
            self._temp_sensor += random.choice(xrange(-2, 2))
            devices.handle_device_update(self.device_id, source='T', value=self._temp_sensor, time_range=1)
            self._humidity_sensor += random.choice(xrange(-2, 2))
            devices.handle_device_update(self.device_id, source='H', value=self._humidity_sensor, time_range=1)
            self._humidity_sensor = random.choice(xrange(0, 100))
            devices.handle_device_update(self.device_id, source='L', value=self._light_sensor, time_range=1)
            self._motion_sensor = random.choice([0, 1])
            devices.handle_device_update(self.device_id, source='M', value=self._motion_sensor, time_range=1)
            self._gas_sensor = random.choice(xrange(0, 100))
            devices.handle_device_update(self.device_id, source='G', value=self._gas_sensor, time_range=1)

# simulated motes - key is the serial
_motes = {}


def initialize(rest_client):
    """
    Initialize mote for simulation

    :param rest_client: REST client to use to communicate with the server.
    :param username: Profile id
    :param create_count: Number of motes to create
    :return: None
    """

    global _motes

    # load devices by querying cloud server
    devices = rest_client.get_devices()
    for device in devices:
        device_id = device['id']
        device_type = device['type']
        _motes[device_id] = _Mote(device_id=device_id, serial=None, device_type=device_type)


def set_device_value(device_id, value):
    global _motes
    _motes[device_id].set_value(value)


def get_device_value(device_id, source):
    global _motes
    return _motes[device_id].get_value(source)


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
            _motes[device_id].simulate()

        # Sleep for random interval
        time.sleep(random.choice(range(total_motes * 3)))
