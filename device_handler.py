"""
This module handles communicating with the devices connected over wireless such as issuing commands that received from server and
send status messages received from devices to server.
"""
import logging
from ServerCommands import ServerCommands

rest_client = None

def _set_device_status(device_id, value):
    """
    Do the necessary thing to change value of a device.
     ie 1) Send coap request to the device.
        2) Once the device acks send the result back to the server through REST.
    """

    #XXX - For debugging loop back
    handle_device_update(device_id, 1, value)

    return


def _get_device_status(device_id, value):
    """
    Do the necessary thing to change value of a device.
     ie 1) Send coap request to the device to get the status
        2) Send the status back using REST.
    """
    return


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
            _set_device_status(args['device_id'], args['value'])
        if command == ServerCommands.GET_DEVICE_STATUS:
            _set_device_status(args['device_id'])
        elif command == ServerCommands.EXECUTE_ACTION:
            _execute_action(args['action_id'])
        elif command == ServerCommands.RECONNECT:
            _reconnect()
    except Exception as e:
        logging.error(e)
        #TODO - I am not sure what todo here?

    return True


def handle_device_update(device_id, status, time_range):
    """
    When a device status(motion detected, lamp on etc) is changed it should be send to server.
    The server then send the status to interested parties.

    This function will be called by coap stack.
    """
    global rest_client

    logging.info('Status update from device :{0} {1}'.format(device_id, status))
    rest_client.send_device_status(device_id, time_range, status)

