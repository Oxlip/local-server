#!/usr/bin/env python
"""
A simple program to send COAP request with CLI.
"""

import argparse

from pycoap.coap.coap import Coap

def process_command_line():
    """
    Process command line arguments and assign to appropriate variable
    """
    parser = argparse.ArgumentParser(description='Send COAP messages.')
    parser.add_argument('--ip', default='aaaa::f4:ac6a:12:4b00', help='Sets ip of the device.')
    parser.add_argument('--node', default='dev/led', help='Sets the node to work with.')
    parser.add_argument('--method', default='get', help='Sets the method to use.')
    parser.add_argument('--data', default='red on', help='Data to send with post/put.')

    return parser.parse_args()




def main():
    args = process_command_line()
    c = Coap(args.ip)
    if args.method == 'get':
        print c.get(args.node).payload
    elif args.method == 'post':
        c.post(args.node, payload=args.data).payload
    else:
        print 'Not implemented yet'
    c.destroy()
    

if __name__ == '__main__':
    main()
