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
             'iz set wpan0 0x5449 0x19 11',
             'ip link add link wpan0 name lowpan0 type lowpan',
             #'ip addr add ' + ip + ' scope global dev lowpan0',
             # need a global addr
             'ip addr add aaaa:0000:0000:0000:00f4:ac6a:0012:4b01 scope global dev lowpan0',
             'ip link set wpan0 up',
             'ip link set lowpan0 up',
             'route -A inet6 add ' + ip + '/64 dev lowpan0',
             'echo 1 > /proc/sys/net/ipv6/conf/all/forwarding',
             'sysctl -w net.ipv6.conf.lowpan0.rpl_dodag_root=1',
             'sysctl -w net.ipv6.conf.lowpan0.rpl_enabled=1']

    for cmd in cmds:
        os.system(cmd)

