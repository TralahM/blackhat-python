#!/usr/bin/env python
"""A Simple TCP Client."""
import socket

target_host = "www.google.com"
target_port = 80


def main(target_host: str, target_port: int = 80):
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    client.connect((target_host, target_port))

    client.send(b"GET / HTTP/1.1\r\nHost: google.com\r\n\r\n")

    response = client.recv(4096)

    print(response.decode("utf8"))


if __name__ == "__main__":
    from argparse import ArgumentParser

    parser = ArgumentParser()
    parser.add_argument(
        "host", action="store", default="www.google.com", help="host to connect to."
    )
    parser.add_argument(
        "port",
        action="store",
        default=80,
        type=int,
        help="port of the host to connect to.",
    )
    args = parser.parse_args()
    host, port = args.host, args.port
    main(host, port)
