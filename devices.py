"""
This module handles communicating with the devices connected over wireless such as issuing commands that received from server and
send status messages received from devices to server.
"""
import logging
import simulation
import json
from ServerCommands import ServerCommands
from pycoap.coap.coap import Coap
from pycoap.coap.message import MessageStatus

rest_client = None
db = None
border_router_ip = None

simulation_mode = False


class DeviceTypes:
    """
    Type of devices
    """
    UHUB = 'uHub'
    UPLUG = 'uPlug'
    USENSE = 'uSense'
    USWITCH = 'uSwitch'


class DeviceValueSource:
    """
    # B - Button(value in percentage 0-100)
    # CA - Current Sensor(value in mA)
    # CS - Current Sensor Summary(peak, active etc in json format)
    # T - Temperature sensor(value in F)
    # M - Motion sensor(value = 0 - no motion)
    # H - Humidity sensor(value in percentage 0-100)
    # L - Light sensor(value in lux)
    # G - Gas sensor (value in percentage)
    """
    BUTTON = 'B'
    CURRENT_AMPS = 'CA'
    CURRENT_SUMMARY = 'CS'
    TEMPERATURE = 'T'
    MOTION = 'M'
    HUMIDITY = 'H'
    LIGHT = 'L'
    GAS = 'G'


def _set_dev_pwr_dim(ip, device_id, dimmer, percentage):
    """
    Set dimmer percentage
    """
    try:
        c = Coap(ip)
        node = 'dev/pwr/{dimmer}/dim'.format(dimmer=dimmer)
        result = c.put(node, payload=str(percentage))
        if result.status != MessageStatus.success:
            err_msg = 'PUT {0} failed {1} {2}'.format(node, result.status, result.payload)
            logging.error(err_msg)
            return result.status
        c.destroy()
        rest_client.send_device_value(device_id=device_id, time_range=1,
                                      source=DeviceValueSource.BUTTON, value=percentage)
    except Exception, e:
        logging.error(e)
        return None

    return result.status


def _set_device_value(device_id, value):
    """
    Do the necessary thing to change value of a device.
     ie 1) Send coap request to the device.
        2) Once the device acks send the result back to the server through REST.
    """
    if simulation_mode:
        simulation.set_device_value(device_id, value)
    else:
        dev = db.get_device(device_id)
        """
        For now we can issue command only to uHub and uSwitch.
        """
        if dev.type == DeviceTypes.UPLUG or dev.type == DeviceTypes.USWITCH:
            if dev.sub_identification:
                sub_dev = dev.sub_identification
            else:
                sub_dev = 0
            _set_dev_pwr_dim(dev.ip, device_id, sub_dev, value)
        else:
            logging.error('Cant set device type - {0}'.format(dev.type))
    return


def _get_device_value(device_id):
    """
    Do the necessary thing to change value of a device.
     ie 1) Send coap request to the device to get the status
        2) Send the status back using REST.
    """
    if simulation_mode:
        value = simulation.get_device_value(device_id)
        time_range = None
        source = 'C'
    else:
        #TODO - issue CoAP to motes or send REST messages to the devices(wemo. hue etc)
        status = ''
        time_range = None
        source = 'C'

    rest_client.send_device_value(device_id=device_id, time_range=None, source=source, value=value)


def _execute_action(action_id):
    """
    Do the necessary thing to execute the given action.
     ie 1) Find all devices involved in this action
        2) Send value to each device.
        3) Collect result and send back to server.
    """
    return


def _reconnect():
    return


def handle_server_command(message):
    """
    When a notification arrives this function is called to process the message.
    """
    logging.debug(str(message))
    try:
        command = int(message['command'])
        args = message['args']
        if command == ServerCommands.SET_DEVICE_STATUS:
            _set_device_value(args['device_id'], args['value'])
        if command == ServerCommands.GET_DEVICE_STATUS:
            _get_device_value(args['device_id'])
        elif command == ServerCommands.EXECUTE_ACTION:
            _execute_action(args['action_id'])
        elif command == ServerCommands.RECONNECT:
            _reconnect()
    except Exception as e:
        logging.error(e)
        #TODO - I am not sure what todo here?

    return True


def handle_device_update(device_id, source, value, time_range):
    """
    When a device status(motion detected, lamp on etc) is changed it should be send to server.
    The server then send the status to interested parties.

    This function will be called by coap stack.
    """

    global rest_client

    logging.info('Sending device value to cloud:{0} source {1} value {1}'.format(device_id, source, value))
    rest_client.send_device_value(device_id, time_range, source, value)

