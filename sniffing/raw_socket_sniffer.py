#!/usr/bin/env python
"""Raw Socket Sniffer for Windows and Linux Platforms."""
import socket
import os
import argparse


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
    while True:
        try:
            data, addr = sniffer.recvfrom(65565)
            print(data, "\n", addr)
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
