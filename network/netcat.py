#!/usr/bin/env python
r"""Netcat utility Knife for networking.

netcat.py -t 192.168.0.1 -p 5555 -l -c
netcat.py -t 192.168.0.1 -p 5555 -l -u \"C:\\\\target.exe\"
netcat.py -t 192.168.0.1 -p 5555 -l -e \"cat /etc/passwd\"
"""
import socket
import sys
import argparse
import threading
import subprocess

# some global Variables

examples = """-------Examples:--------\n
netcat.py -t 192.168.0.1 -p 5555 -l -c
netcat.py -t 192.168.0.1 -p 5555 -l -u \"C:\\\\target.exe\"
netcat.py -t 192.168.0.1 -p 5555 -l -e \"cat /etc/passwd\"
"""


def client_handler(client_socket, upload_destination="", execute="", command=False):
    """Handle Client Upload, Execution,or Shell Command Requests."""
    # check for upload
    if len(upload_destination):
        # read in all of the bytes and write to our destination
        file_buffer = ""
        # keep reading data until none is available
        while True:
            data = client_socket.recv(1024)
            if not data:
                break
            else:
                file_buffer += data

        # now we take these bytes and try to write them out
        try:
            file_descriptor = open(upload_destination, "wb")
            file_descriptor.write(file_buffer)
            file_descriptor.close()
            # acknowledge that we wrote the file out
            client_socket.send(
                b"Successfully saved file to %s \r\n" % upload_destination,
            )
        except Exception as e:
            client_socket.send(
                b"\n%s\r\nFailed to save file to %s\r\n" % (
                    str(e), upload_destination),
            )
    # check for command execution
    if len(execute):
        # run the command
        output = run_command(execute)
        client_socket.send(output)

    # now we go into another loop if a shell was requested
    if command:
        while True:
            # show a simple prompt
            client_socket.send(b">>>\r")
            # now we receive until we see a line feed
            cmd_buffer = ""
            while "\n" not in cmd_buffer:
                cmd_buffer += client_socket.recv(1024).decode()
            # send back the command output
            response = run_command(cmd_buffer)
            # send back the response
            client_socket.send(response)


def server_loop(args: argparse.Namespace):
    """Primary server loop.

    To handle both our command execution and our full command shell.
    If no Target Host is specified we listen on all interfaces.
    If no Target Port is specified we listen on port 12345.
    """
    target_host, target_port = args.target_host, args.target_port
    if not target_host:
        target_host = "0.0.0.0"
    if not target_port:
        target_port = 12345
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((target_host, target_port))
    server.listen(5)
    print(f"Listening on {target_host}:{target_port} ...")

    while True:
        client_socket, addr = server.accept()
        print(f"Accepted {addr[0]}:{addr[1]} ...")
        # spin off a thread to handle our new client
        client_thread = threading.Thread(
            target=client_handler,
            args=(client_socket, args.upload_destination,
                  args.execute, args.command),
        )
        client_thread.start()


def run_command(command):
    """Run the Given Command and return the STDOUT Output."""
    # trim the newline
    command = command.rstrip()
    # run the command
    try:
        output = subprocess.check_output(
            command, stderr=subprocess.STDOUT, shell=True)
    except Exception as e:
        output = f"Failed with: {str(e)}\r\n"
        output = bytes(output, "utf8")
    # send output back to the client
    return output


def client_sender(buffer, target_host, target_port):
    """Netcat Client Code."""
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        # connect to our target host
        client.connect((target_host, target_port))
        if len(buffer):
            buffer = bytes(buffer, "utf8")
            client.send(buffer)
        while True:
            # now wait for data back
            recv_len, response = 1, b""
            while recv_len:
                data = client.recv(4096)
                recv_len = len(data)
                response += data
                if recv_len < 4096:
                    break
            print(response.decode())
            # wait for more input
            buffer = input("")
            buffer += "\n"
            # send if off
            buffer = bytes(buffer, "utf8")
            client.send(buffer)

    except Exception as e:
        print(f"[*] Exception!! {e} Exiting...")
        # tear down the connection
        client.close()
        # raise e


def main(args: argparse.Namespace):
    """Receive CLI args and execute main Netcat Program Logic."""
    # Are we going to listen or just send data from stdin
    if not args.listen and args.target_host and args.target_port:
        # read in the buffer from the command line, send CTRL-D if not sending
        # input to stdin as this is blocking.
        print("<Hit CTRL-D> ")
        buffer = sys.stdin.read()
        # buffer = bytes(input(">>> "), "utf8")
        # send data off
        client_sender(buffer, args.target_host, args.target_port)
    # We are going to listen and potentially upload things, execute commands,
    # and drop a shell back depending on the command line options above.
    if args.listen:
        server_loop(args)
    pass


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        prog="Netcat Swiss Army Knife.",
        usage=examples,
    )
    parser.add_argument(
        "-t",
        "--target-host",
        action="store",
        dest="target_host",
        default=None,
        help="target host",
    )
    parser.add_argument(
        "-p",
        "--port",
        action="store",
        dest="target_port",
        default=None,
        type=int,
        help="target port",
    )
    parser.add_argument(
        "-l",
        "--listen",
        action="store_true",
        default=False,
        dest="listen",
        help="Listen on [target_host]:[target_port] for incoming connections",
    )
    parser.add_argument(
        "-c",
        "--command",
        action="store_true",
        default=False,
        dest="command",
        help="Initialize a Command Shell",
    )
    parser.add_argument(
        "-e",
        "--execute",
        action="store",
        default="",
        dest="execute",
        help="Execute the given command|file upon receiving a connection",
    )
    parser.add_argument(
        "-u",
        "--upload-destination",
        action="store",
        default="",
        dest="upload_destination",
        help="Upon receiving connection upload a file and write to [upload_destination]",
    )
    args = parser.parse_args()
    # print(type(args), args)
    main(args)
