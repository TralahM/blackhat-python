#!/usr/bin/env python
"""Paramiko SSH Command."""
import paramiko
import subprocess
import threading
import getpass


def ssh_command(ip, user, passwd, command):
    client = paramiko.SSHClient()
    # client.load_host_keys("/home/root/.ssh/known_hosts")
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect(ip, username=user, password=passwd)
    ssh_session = client.get_transport().open_session()
    if ssh_session.active:
        ssh_session.exec_command(command)
        print(ssh_session.recv(1024).decode())
    return


user = getpass.getuser()
passwd = getpass.getpass("password:")
ssh_command("localhost", user, passwd, "id")
