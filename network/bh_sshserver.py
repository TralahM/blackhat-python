#!/usr/bin/env python
"""SSH Server."""
import socket
import paramiko
import threading
import sys

# using the key from the Paramiko demo files
host_key = paramiko.RSAKey(filename="test_rsa.key")


class Server(paramiko.ServerInterface):
    """Paramiko Server Interface."""

    def __init__(self):
        self.event = threading.Event()

    def check_channel_request(self, kind, chanid):
        if kind == "session":
            return paramiko.OPEN_SUCCEEDED
        return paramiko.OPEN_FAILED_ADMINISTRATIVELY_PROHIBITED

    def check_auth_password(self, username, password):
        if (username in ["root", "african"]) and password is not None:
            return paramiko.AUTH_SUCCESSFUL
        return paramiko.AUTH_FAILED


if __name__ == "__main__":
    from argparse import ArgumentParser

    parser = ArgumentParser()
    parser.add_argument(
        "-s",
        "--server",
        action="store",
        dest="server",
        help="server ip",
    )
    parser.add_argument(
        "-p",
        "--port",
        action="store",
        dest="port",
        help="server port",
    )
    args = parser.parse_args()
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        sock.bind((args.server, args.port))
        sock.listen(100)
        print("[+] Listening for conections ...")
        client, addr = sock.accept()
    except Exception as e:
        print(f"[-] Listen failed: {e}")
        sys.exit(1)
    print("[+] Got a Connection!")
    try:
        bhSession = paramiko.Transport(client)
        bhSession.add_server_key(host_key)
        server = Server()
        try:
            bhSession.start_server(server=server)
        except paramiko.SSHException as e:
            print(f"[-] Host Negotiation Failed: {e}")
        chan = bhSession.accept(20)
        print("[+] Authenticated!")
        print(chan.recv(1024))
        chan.send("Welcom to bh_ssh")
        while True:
            try:
                command = input("Enter CMD: ").strip("\n")
                if command != "exit":
                    chan.send(command)
                    print(chan.recv(1024).decode() + "\n")
                else:
                    chan.send(b"exit")
                    print("Exiting..")
                    bhSession.close()
                    raise Exception("Exit")
            except KeyboardInterrupt:
                bhSession.close()
    except Exception as e:
        print(f"[-] Caught exception {e}")
        try:
            bhSession.close()
        except Exception:
            pass
        sys.exit(1)
