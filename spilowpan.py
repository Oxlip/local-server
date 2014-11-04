#! /usr/bin/python
""" Do 6lowpan over SPI
"""

import os
import socket
import select
import serial
import struct
import logging
import argparse
import binascii
import ipaddress


def create_lowpan(ip, driver='at86rf230'):
    print 'IP: ' + ip
    cmds = [ 'modprobe ' + driver,
             'iz add wpan-phy0 wpan0 00:00:00:00:00:00:00:01',
             'iz set wpan0 0x999 0x1 11',
             'ip link add link wpan0 name lowpan0 type lowpan',
             'ip addr add ' + ip + ' dev lowpan0',
             'ip link set wpan0 up',
             'ip link set lowpan0 up' ]

    for cmd in cmds:
        os.system(cmd)

