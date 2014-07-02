#!/usr/bin/env python

"""
The main program which binds everything else.
"""
import signal
import sys
import argparse
import logging
import time
import gevent

from pycoap.coap import coap
from database import Database, reset_tables
from rest_client import RestClient
import notifications
import tunslip
import device_handler


def process_command_line():
    """
    Process command line arguments and assign to appropriate variable
    """
    parser = argparse.ArgumentParser(description='PlugZ Hub.')
    parser.add_argument('--verbose', default=0, help='Increases the logging amount.')
    parser.add_argument('--factory-reset', default=0, help='Erases the hub configuration.')
    return parser.parse_args()


def get_hub_identity():
    """
    Reads IDPROM and returns hub identifier
    """
    # TODO - implement reading from beaglebone IDPROM
    # For now this is a test data (same as backend/models/ExampleData.SQL)
    return 'AABBCCDDEEG2', 'AUTH_KEY IS EMPTY'


def _get_br_ip_address():
    """ Helper function to get Border router's IP address.
    """
    while True:
        time.sleep(1)
        br_ip_address = tunslip.get_br_ip_address()
        if br_ip_address:
            break
    return br_ip_address


def signal_handler(signal, frame):
    logging.info('Ctl+C signal receive - Terminating PlugZ-Hub.')
    sys.exit(0)


def main():
    args = process_command_line()
    logging.basicConfig(level=int(args.verbose))

    signal.signal(signal.SIGINT, signal_handler)

    hub_identity, authentication_key = get_hub_identity()
    rest_client = RestClient(hub_identity, authentication_key)

    if args.factory_reset:
        logging.info('Resetting device information')
        reset_tables(hub_identity, rest_client.hub_id)

    db = Database(rest_client)
    device_handler.rest_client = rest_client

    _greenlets = [gevent.spawn(notifications.notification_loop, rest_client.channel_id),
                  gevent.spawn(tunslip.tunslip_loop)]

    br_ip_address = _get_br_ip_address()

    gevent.joinall(_greenlets)

    logging.info('Terminating PlugZ-Hub.')

main()
