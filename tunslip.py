#! /usr/bin/python
""" SLIP using TUN interface.
"""
import os
from fcntl import ioctl
import threading
import socket
import select
import serial
import struct
import logging
import argparse
import binascii
import ipaddress

TUNSETIFF = 0x400454ca
IFF_TUN = 0x0001
IFF_TAP = 0x0002
IFF_NO_PI = 0x1000

IPV6PREFIX = 'aaaa::'

SLIP_END = 0xc0
SLIP_ESC = 0xdb
SLIP_ESC_END = 0xdc
SLIP_ESC_ESC = 0xdd
DEBUG_MSG_START = 0x0d
DEBUG_MSG_END = 0x0a

SLIP_DEVICE = '/dev/ttyACM0'
DEFAULT_BAUD_RATE = 115200

ser_dev = None
_br_ip6_address = None

def _create_tun(ipv6_prefix):
    """ Creates tunnel interface and sets up route entries.
    """
    # create virtual interface
    tun_fd = os.open('/dev/net/tun', os.O_RDWR)
    ifname = 'tun0'
    ifr = struct.pack('16sH', ifname, IFF_TUN | IFF_NO_PI)
    ioctl(tun_fd, TUNSETIFF, ifr)

    # configure IPv6 address
    os.system('ifconfig ' + ifname + ' inet add ' + ipv6_prefix + '/128')
    os.system('ifconfig ' + ifname + ' inet6 add fe80::0:0:0:0/64')
    os.system('ifconfig ' + ifname + ' up')

    # add route and enable IPv6 forwarding
    os.system('route -A inet6 add ' + ipv6_prefix + '/64 dev ' + ifname)
    os.system('echo 1 > /proc/sys/net/ipv6/conf/all/forwarding')

    logging.info('\nCreated following virtual interface:')
    os.system('ifconfig ' + ifname)
    return tun_fd


def _slip_encode(sting):
    """ Encodes the given IP packet as per SLIP protocol.
    """
    result = bytearray()

    result.append(SLIP_END)
    for i in sting:
        i = ord(i)
        if i == SLIP_END:
            result += bytearray([SLIP_ESC, SLIP_ESC_END])
        elif i == SLIP_ESC:
            result += bytearray([SLIP_ESC, SLIP_ESC_ESC])
        else:
            result.append(i)

    # Mark end of SLIP packet
    result.append(SLIP_END)
    return result


def _slip_decode(serial_dev):
    """ Decodes the given SLIP packet into IP packet.
    """
    debug_msg = []
    decoded = []
    while True:
        char = serial_dev.read()
        byte = ord(char)
        if byte == SLIP_END:
            break
        elif byte == SLIP_ESC:
            char = serial_dev.read()
            if char is None:
                logging.error("Protocol Error")
                break
            byte = ord(char)
            if byte == SLIP_ESC_END:
                decoded.append(SLIP_END)
            elif byte == SLIP_ESC_ESC:
                decoded.append(SLIP_ESC)
            elif byte == DEBUG_MSG_START:
                decoded.append(DEBUG_MSG_START)
            elif byte == DEBUG_MSG_END:
                decoded.append(DEBUG_MSG_END)
            else:
                logging.error("Protocol Error")
        elif byte == DEBUG_MSG_START and len(decoded) == 0:
            while True:
                char = serial_dev.read()
                byte = ord(char)
                if byte == DEBUG_MSG_END or byte == SLIP_END:
                    break
                debug_msg.append(byte)
        else:
            decoded.append(byte)

    return decoded, debug_msg


def _serial_to_tun(ser_dev, tun_fd):
    """ Processes packets from serial port and sends them over tunnel.
    """
    data, debug_msg = _slip_decode(ser_dev)

    if len(debug_msg) > 0:
        for line in str(bytearray(debug_msg)).split('\n'):
            logging.debug('serial>   {0}'.format(line))

    if len(data) <= 0:
        return

    bdata = bytearray(data)
    if bdata == b'?P':
        """ Prefix info requested
        """
        raw_prefix = socket.inet_pton(socket.AF_INET6, IPV6PREFIX)
        prefix = _slip_encode('!P' + raw_prefix)
        logging.info('Sending IPv6 Prefix - {0} len {1}'.format(binascii.hexlify(raw_prefix), len(raw_prefix)))
        ser_dev.write(prefix)
        return

    if bytearray(data[0:2]) == b'!I':
        """ Prefix info requested
        """
        if len(data) <= 2:
            # if we got
            return
        global _br_ip6_address
        _br_ip6_address = ipaddress.IPv6Address(bytes(bytearray(data[2:])))
        logging.debug('Border router IP address {0}'.format(str(_br_ip6_address)))
        return

    try:
        os.write(tun_fd, bdata)
    except Exception, e:
        logging.error('_serial_to_tun() write exception {0} data=[{1}]'.format(str(e), bdata))
        pass


def _tun_to_serial(tun_fd, ser_dev):
    """ Processes packets from tunnel and sends them over serial.
    """
    data = os.read(tun_fd, 4096)
    if data:
        ser_dev.write(str(_slip_encode(data)))
    else:
        logging.error('Failed to read from TUN')


def _tunslip_loop(ipv6_prefix):
    """
    Transmits packets received from serial to ip tunnel and vice versa, forever.
    """
    global ser_dev
    ser_dev = serial.Serial(SLIP_DEVICE, DEFAULT_BAUD_RATE)
    ser_dev.write(serial.to_bytes([SLIP_END]))

    tun_fd = _create_tun(ipv6_prefix)
    while True:
        read_fds = [ser_dev.fileno(), tun_fd]
        read_ready, write_ready, err = select.select(read_fds, [], [])
        for fd in read_ready:
            if fd == tun_fd:
                _tun_to_serial(tun_fd, ser_dev)

            if fd == ser_dev.fileno():
                _serial_to_tun(ser_dev, tun_fd)


def start_tunslip_thread(prefix=IPV6PREFIX):
    """
    Start SLIP tunnel processing as a separate thread.
    """
    slip_thread = threading.Thread(target=_tunslip_loop, args=(prefix,))
    slip_thread.daemon = True
    slip_thread.start()

    return slip_thread


def get_br_ip_address():
    """ Returns IPv6 address of the border router CC2538
    """
    global _br_ip6_address, ser_dev
    # if border router address is yet received, then send a request to get one.
    if _br_ip6_address is None:
        if ser_dev is not None:
            ser_dev.write(_slip_encode('?I'))
    return _br_ip6_address


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-v', '--verbose', action='store_true',
                        help='Sets logging level to high.')
    parser.add_argument('-s', '--serial-device', default='/dev/ttyACM0',
                        help='Serial device path - Eg: /dev/ttyACM0')
    parser.add_argument('-b', '--baud-rate', default=DEFAULT_BAUD_RATE, type=int,
                        help='Baudrate of the UART')

    args = parser.parse_args()
    logging.basicConfig(level=logging.DEBUG if args.verbose else logging.INFO)

    _tunslip_loop(IPV6PREFIX)


if __name__ == "__main__":
    main()
