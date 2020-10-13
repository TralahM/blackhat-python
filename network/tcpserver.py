#!/usr/bin/env python
"""A Simple TCP Server."""
import socket
import threading


def spawn_server(bind_port: int = 9999, bind_ip: str = "0.0.0.0"):
    """Spawn a Server Socket Listening for upto 5 Clients."""
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((bind_ip, bind_port))
    server.listen(5)
    print(f"[*] Listening on {bind_ip}:{bind_port} ...")
    return server


def handle_client(client_socket):
    """Handle a Connected Client Socket."""
    request = client_socket.recv(1024)
    print(f"[*] Received: {request}")
    client_socket.send(b"ACK!")
    client_socket.close()


def main(bind_ip, bind_port):
    """Execute the Main Program Logic of Client-Server Communication."""
    server = spawn_server(bind_port, bind_ip)
    while True:
        client, addr = server.accept()
        print(f"[*] Accepted Connection from {addr[0]}:{addr[1]}")
        client_handler = threading.Thread(target=handle_client, args=(client,))
        client_handler.start()


if __name__ == "__main__":
    from argparse import ArgumentParser

    parser = ArgumentParser()
    parser.add_argument(
        "-s",
        "--shost",
        action="store",
        default="0.0.0.0",
        dest="host",
        help="host to bind to.",
    )
    parser.add_argument(
        "--p",
        "--port",
        action="store",
        default=9000,
        dest="port",
        type=int,
        help="port of the host to bind to.",
    )
    args = parser.parse_args()
    host, port = args.host, args.port
    main(host, port)
