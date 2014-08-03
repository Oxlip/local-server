#!/usr/bin/env python

"""
The main program which binds everything else.
"""
import gevent.monkey
gevent.monkey.patch_all()
import signal
import sys
import argparse
import logging
import time
import json

from pycoap.coap.coap import Coap

from database import Database, reset_tables
from rest_client import RestClient
import tunslip
import devices
import simulation

_border_router_ip = None
_discovered_motes = {}


def get_hub_identity():
    """
    Reads IDPROM and returns hub identifier
    """
    # TODO - implement reading from beaglebone IDPROM
    # For now this is a test data (same as backend/models/ExampleData.SQL)
    return 'T3TBGRZ5PW', 'AUTH_KEY IS EMPTY'


def get_br_ip_address():
    """ Helper function to get Border router's IP address.
    """
    global _border_router_ip
    if _border_router_ip:
        return _border_router_ip
    while True:
        time.sleep(1)
        _border_router_ip = tunslip.get_br_ip_address()
        if _border_router_ip:
            return _border_router_ip


def _get_mote_info(mote_ip):
    """ Returns mote information by using IPSO COAP nodes.
    """
    c = Coap(mote_ip)
    payload = str(c.get('dev/ser').payload)
    c.destroy()

    return payload


def _local_scan_loop(br_ip_address):
    """ Scans local network every one second for new devices.
    """
    global _discovered_motes
    c = Coap(str(br_ip_address))
    while True:
        try:
            count = int(c.get('rplinfo/routes').payload)
            print '{0} motes connected to the uHub'.format(count)
            for i in range(count):
                payload = str(c.get('rplinfo/routes?index={0}'.format(i)).payload)
                print 'rplinfo/routes?index={0}'.format(i), payload
                result = json.loads(payload)
                mote_ip = result['dest']
                if mote_ip in _discovered_motes:
                    print mote_ip, 'already exists ', _get_mote_info(mote_ip)
                else:
                    _discovered_motes[mote_ip] = _get_mote_info(mote_ip)
                    print 'new discovery ', mote_ip

        except Exception, e:
            raise
        else:
            pass
        finally:
            pass
        time.sleep(10)
    c.destroy()
    return


def _notification_loop(channel_id):
    """
    Process push notifications in a loop
    """
    import PubNub
    from devices import handle_server_command

    # TODO - Replace the publish key and subscribe key
    pubnub = PubNub.Pubnub(publish_key='pub-c-9ff29ff2-1427-4864-bbfa-7d3270a233dc',
                           subscribe_key='sub-c-7e20413a-8d2d-11e3-ae86-02ee2ddab7fe',
                           ssl_on=False)
    pubnub.subscribe({
        'channel': channel_id,
        'callback': handle_server_command
    })


def signal_handler(signal, frame):
    logging.info('Ctl+C signal receive - Terminating PlugZ-Hub.')
    import gc
    import traceback
    from greenlet import greenlet

    for ob in gc.get_objects():
        if not isinstance(ob, greenlet):
            continue
        if not ob:
            continue
        logging.debug(''.join(traceback.format_stack(ob.gr_frame)))
    sys.exit(0)


def process_command_line():
    """
    Process command line arguments and assign to appropriate variable
    """
    parser = argparse.ArgumentParser(description='PlugZ Hub.')
    parser.add_argument('--verbose', default=100, help='Sets the logging amount.')
    parser.add_argument('--coap-log', default=100, help='Sets coap logging amount.')
    parser.add_argument('--simulation', action='store_true', help='Simulates WSN and does not connect to real WSN.')
    parser.add_argument('--factory-reset', default=0, help='Erases the hub configuration.')
    return parser.parse_args()


def main():
    args = process_command_line()
    logging.basicConfig(level=int(args.verbose))
    coap_logger = logging.getLogger('coap')
    coap_logger.setLevel(int(args.coap_log))

    signal.signal(signal.SIGINT, signal_handler)

    hub_identity, authentication_key = get_hub_identity()
    rest_client = RestClient(hub_identity, authentication_key)

    if args.factory_reset:
        logging.info('Resetting device information')
        reset_tables(hub_identity, rest_client.hub_id)

    db = Database(rest_client)
    devices.rest_client = rest_client

    logging.info('Simulation: {0}'.format('on' if args.simulation else 'off'))
    _greenlets = [gevent.spawn(_notification_loop, rest_client.channel_id)]
    _greenlets = []
    if args.simulation:
        devices.simulation_mode = True
        simulation.initialize(rest_client)
        _greenlets.append(gevent.spawn(simulation.simulation_loop))
    else:
        _greenlets.append(gevent.spawn(tunslip.tunslip_loop))
        devices.border_router_ip = get_br_ip_address()
        logging.debug('Border router IP {0}'.format(get_br_ip_address()))

    _greenlets.append(gevent.spawn(_local_scan_loop, get_br_ip_address()))

    gevent.joinall(_greenlets)

    logging.info('Terminating PlugZ-Hub.')

main()
