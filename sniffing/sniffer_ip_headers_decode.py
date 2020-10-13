#!/usr/bin/env python
"""Decode the entire IP header.

We Decode the entire IP header (except the Options field) and extract the
protocol type,source, and destination IP address.
"""
import os
import struct
import socket
import argparse
from ctypes import *


class ByKeyOrValue(object):
    _set_of_pairs = set()

    @classmethod
    def get(cls, key_or_value, default="Unknown"):
        for pair in cls._set_of_pairs:
            if pair[0] == key_or_value:
                return pair[1]
            elif pair[1] == key_or_value:
                return pair[0]

        return default


class EtherTypes(ByKeyOrValue):
    _set_of_pairs = {
        ("IPv4", 0x0800),
        ("ARP", 0x0806),
        ("RARP", 0x8035),
        ("SNMP", 0x814C),
        ("IPv6", 0x86DD),
    }


class IPVersions(ByKeyOrValue):
    _set_of_pairs = {("IPv4", 4), ("IPv6", 6)}


class TransportProtocols(ByKeyOrValue):
    _set_of_pairs = {("ICMP", 1), ("TCP", 6), ("UDP", 17)}


# Header and footer formatting functions
def print_section_header(s):
    print("{:=^78}".format(" " + s + " "))


def print_section_footer():
    print("{:=^78}\n".format(""))


def print_output(label, format_str, *format_values):
    print(("{:<30} " + format_str).format(label, *format_values))


def format_field(field, field_type):

    if field_type == "mac":
        # Format a MAC address as XX:XX:XX:XX:XX:XX
        byte_str = ["{:02x}".format(field[i]) for i in range(0, len(field))]
        return ":".join(byte_str)
    elif field_type == "ethertype":
        return EtherTypes.get(field)
    elif field_type == "ipver":
        return IPVersions.get(field)
    elif field_type == "transproto":
        return TransportProtocols.get(field)


class IPFlags(object):
    def __init__(self, flag_bits):
        # Flags is an integer taking 3-bit
        # The 1st bit is reserved and is of no use
        # The 2nd bit:
        self.DF = flag_bits & 0b11 >> 1
        # The 3rd bit:
        self.MF = flag_bits & 0b1

    def __str__(self):
        result = []
        if self.DF:
            result.append("DF, ")
        if self.MF:
            result.append("MF, ")

        "".join(result)

        if result:
            return result[:-2]
        else:
            return "--"


class IP:
    def __init__(self, socket_buffer=None):
        # map protocol constants to their names
        self.protocol_map = {1: "ICMP", 6: "TCP", 17: "UDP"}
        hdr_str = socket_buffer[14:34]
        hdr_unpacked = struct.unpack("!BBHHHBBH4s4s", hdr_str)
        self.ver = hdr_unpacked[0] >> 4  # High 4 bits
        # Low 4 bits hold header length in 32-bit words;
        # By multiplying by four 32-bit words are converted to bytes
        self.hdr_size = (hdr_unpacked[0] & 0b1111) * 4
        self.dscp = hdr_unpacked[1] >> 6  # High 6 bits
        self.ecn = hdr_unpacked[1] & 0b11  # Low 2 bits
        self.tlen = hdr_unpacked[2]
        self.id = hdr_unpacked[3]
        self.flags = IPFlags(hdr_unpacked[4] >> 3)
        # Low 13 bits
        self.fragoff = hdr_unpacked[4] & 0b1111111111111
        self.ttl = hdr_unpacked[5]
        self.proto = hdr_unpacked[6]
        self.check_sum = hdr_unpacked[7]
        # human readable IP addresses
        self.src_address = socket.inet_ntoa(hdr_unpacked[8])
        self.dst_address = socket.inet_ntoa(hdr_unpacked[9])
        # human readable protocol
        try:
            self.protocol = self.protocol_map[self.proto]
        except Exception:
            self.protocol = str(self.proto)

    def dump(self, num):
        print_section_header("IP HEADER #{}".format(num))

        print_output("Version", "{} ({})", self.ver,
                     format_field(self.ver, "ipver"))
        print_output("IP Header Length", "{} bytes", self.hdr_size)
        print_output("Diff Services", "{}", self.dscp)
        print_output("Expl Congestion Notification", "{}", self.ecn)
        print_output("Total Length", "{} bytes", self.tlen)
        print_output("Identification", "0x{:04x}", self.id)
        # print_output("Flags", "{}", self.flags)
        print_output("Fragment Offset", "{}", self.fragoff)
        print_output("TTL", "{}", self.ttl)
        print_output("Protocol", "{}", format_field(self.proto, "transproto"))
        print_output("Checksum", "0x{:04x}", self.check_sum)
        print_output("Source IP", "{}", self.src_address)
        print_output("Destination IP", "{}", self.dst_address)
        print_section_footer()


def main(args: argparse.Namespace):
    """Run Raw Socket Sniffer."""
    if os.name == "nt":
        socket_protocol = socket.IPPROTO_IP
    else:
        socket_protocol = socket.IPPROTO_ICMP
    sniffer = socket.socket(socket.AF_INET, socket.SOCK_RAW, socket_protocol)
    sniffer.bind((args.host, 0))
    # we want the IP headers included in the capture
    sniffer.setsockopt(socket.IPPROTO_IP, socket.IP_HDRINCL, 1)
    # if on Windows, we need to send an IOCTL to set up promiscuous mode
    if os.name == "nt":
        sniffer.ioctl(socket.SIO_RCVALL, socket.RCVALL_ON)
    # read a single packet
    xc = 1
    while True:
        try:
            data, addr = sniffer.recvfrom(65565)
            # create an IP header from the first 20 bytes of the data buffer
            ip_header = IP(data)
            ip_header.dump(xc)
            xc += 1
            # print(
            #     f"Protocol: {ip_header.protocol} {ip_header.src_address} -> {ip_header.dst_address}"
            # )
            # print(data, "\n", addr)
        except KeyboardInterrupt:
            break
    # if on Windows, turn off promiscuous mode
    if os.name == "nt":
        sniffer.ioctl(socket.SIO_RCVALL, socket.RCVALL_OFF)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-t",
        "--target-host",
        action="store",
        dest="host",
        default="192.168.2.100",
        help="Host To Listen On",
    )
    args = parser.parse_args()
    main(args)
