"""
This module handles communicating with the devices connected over wireless such as issuing commands that received from server and
send status messages received from devices to server.
"""
import logging


def handle_server_commands(command, args):
    logging.info('Command from server :{0} {1}', command, str(args))
    return


def handle_device_update(device_identification, status):
    logging.info('Status update from device :{0} {1}', device_identification, str(status))

