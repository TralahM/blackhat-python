#!/usr/bin/env python
"""A TCP Proxy."""
import sys
import socket
import threading
import argparse


def cord(x):
    return ord(x) if not isinstance(x, int) else x


def hexdump(src, length=16, digits=4):
    """Pretty Hex Dumping Function.

    Directly taken from http://code.activestate.com/recipes/142812-hex-dumper/.
    """
    result = []
    # digits = 4 if isinstance(src, str) else 2
    # digits = 4
    for i in range(0, len(src), length):
        s = src[i: i + length]
        hexa = b" ".join([b"%0*X" % (digits, cord(x)) for x in s])
        if isinstance(src, str):
            text = b"".join(
                [bytes(x, "utf8") if 0x20 <= ord(x)
                 < 0x7F else b"." for x in s]
            )
        else:
            text = b"".join(
                [
                    bytes(chr(cord(x)), "utf8") if 0x20 <= cord(
                        x) < 0x7F else b"."
                    for x in s
                ]
            )
        result.append(
            (b"%0" + b"%dX:" % (digits) + b" %-*s |%s|")
            % (i, length * (2 + 1) + 1, hexa, text)
        )
    print(b"\n".join(result))
    return b"\n".join(result)


def receive_from(connection, timeout=2):
    """Receive local and remote data.

    Default 2 Seconds Timeout which may be aggresive if proxying traffic to
    other countries or over lossy networks, increase the timeout as neccessary.
    """
    buffer = b""
    # we set a 2 second timeout
    connection.settimeout(timeout)
    try:
        # keep reading until there is no more data
        while True:
            data = connection.recv(4096)
            if not data:
                break
            buffer += data
    except Exception as e:
        print(f"{e}")
        pass
    return buffer


def request_handler(buffer):
    """Modify any requests destined for the remote host."""
    # perform packet modifications
    return buffer


def response_handler(buffer):
    """Modify any responses destined for the local host."""
    # perform packet modifications
    return buffer


def server_loop(
    local_host,
    local_port,
    remote_host,
    remote_port,
    receive_first,
):
    """Run the Proxy Server."""
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        server.bind((local_host, local_port))
    except Exception as e:
        print(f"Failed: {str(e)}")
        sys.exit(0)
    print(f"[*] Listening on {local_host}:{local_port}")
    server.listen(5)
    while True:
        client_socket, addr = server.accept()
        print(f"[===>] Received Incoming connection from {addr[0]}:{addr[1]}")
        # start a thread to talk to the remote host
        proxy_thread = threading.Thread(
            target=proxy_handler,
            args=(
                client_socket,
                remote_host,
                remote_port,
                receive_first,
            ),
        )
        proxy_thread.start()


def proxy_handler(client_socket, remote_host, remote_port, receive_first):
    """Proxy Handler Function."""
    remote_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    remote_socket.connect((remote_host, remote_port))
    # receive data from the remote end if necessary
    if receive_first:
        remote_buffer = receive_from(remote_socket)
        hexdump(remote_buffer)
        # send it to our response handler
        remote_buffer = response_handler(remote_buffer)
        # if we have data to send to our local client, send it
        if len(remote_buffer):
            print("[<===] Sending %d bytes to localhost." % len(remote_buffer))
            client_socket.send(remote_buffer)

    # now lets loop and read from local, send to remote, send to local
    # rinse,wash,repeat
    while True:
        # read from local host
        local_buffer = receive_from(client_socket)
        if len(local_buffer):
            print("[===>] Received %d bytes from local host" %
                  len(local_buffer))
            hexdump(local_buffer)
            # send it to our request handler
            local_buffer = request_handler(local_buffer)
            # send off the data to the remote host
            remote_socket.send(local_buffer)
            print("[===>] Sent to Remote.")
        # receive back the response
        remote_buffer = receive_from(remote_socket)
        if len(remote_buffer):
            print("[===>] Received %d bytes from remote host" %
                  len(remote_buffer))
            hexdump(remote_buffer)
            # send it to our response handler
            remote_buffer = response_handler(remote_buffer)
            # send the response to the local socket
            client_socket.send(remote_buffer)
            print("[<===] Sent to LocalHost.")
        # if no more data on either side,close the connections
        if not len(local_buffer) or not len(remote_buffer):
            client_socket.close()
            remote_socket.close()
            print("[*] No more data. Closing connections.")
            break


def main():
    """Run Main CLI Handler."""
    parser = argparse.ArgumentParser(
        prog="TCP Proxy",
    )
    parser.add_argument(
        "-lh",
        "--local-host",
        action="store",
        dest="local_host",
        default=None,
        help="local host",
    )
    parser.add_argument(
        "-lp",
        "--local-port",
        action="store",
        dest="local_port",
        default=None,
        type=int,
        help="local port",
    )
    parser.add_argument(
        "-rh",
        "--remote-host",
        action="store",
        dest="remote_host",
        default=None,
        help="remote host",
    )
    parser.add_argument(
        "-rp",
        "--remote-port",
        action="store",
        dest="remote_port",
        default=None,
        type=int,
        help="remote port",
    )
    parser.add_argument(
        "-R",
        action="store_true",
        default=False,
        dest="receive_first",
        help="Receive First? I.e Try to Receive data from remote first.",
    )
    args = parser.parser_args()
    main(
        args.local_host,
        args.local_port,
        args.remote_host,
        args.remote_port,
        args.receive_first,
    )
