#!/usr/bin/env python

import paramiko
import SocketServer
import traceback
import threading
import argparse
import threading
import socket
import sys

log = open("logs/ssh_log.txt", "a")
host_key = paramiko.RSAKey(filename='keys/private.key')
port = 22
#SSH_BANNER = "SSH-2.0-OpenSSH_8.2p1 Ubuntu-4ubuntu0.3"

class HoneywallSSHServer(paramiko.ServerInterface):
    """Settings for paramiko server interface"""
    def _init_(self):
        self.event = threading.Event()

    def check_channel_request(self, kind, chanid):
        if kind == 'session':
            return paramiko.OPEN_SUCCEEDED
        return paramiko.OPEN_FAILED_ADMINISTRATIVELY_PROHIBITED

    def check_auth_password(self, username, password):
        if (username == 'root') and (password  == 'password123'):
            return paramiko.AUTH_SUCCESSFUL
        return paramiko.AUTH_FAILED

    def get_allowed_auths(self, username):
        return 'password'

    def check_channel_shell_request(self, channel):
        self.event.set()
        return True

    def check_channel_pty_request(self, channel, term, width, height, pixelwidth, pixelheight, modes):
        return True


def Response(command, attackInterface):
    response = ""
    if command.startswith("ls"):
        response = "Desktop   Downloads   text.txt"
    elif command.startswith("pwd"):
        response = "/root"
    elif command.startswith("whoami"):
        response = "root"
    elif command == "help":
        return
    else:
        response = command + ": command not found"
    attackInterface.send(response + "\r\n")


def SSHConnection(client, addr):
    log.write("\n\nConnection from: " + addr[0] + "\n")
    print('Got a connection!')
    try:
        transport = paramiko.Transport(client)
        transport.add_server_key(host_key)
        # Change banner to appear legit on nmap (or other network) scans
        # transport.local_version = SSH_BANNER
        server = HoneywallSSHServer()
        try:
            transport.start_server(server=server)
        except paramiko.SSHException:
            print('SSH connection failed.')

        attackInterface = transport.accept(20)
        if attackInterface is None:
            transport.close()

        server.event.wait(10)
        if not server.event.is_set():
            transport.close()

        try:
            attackInterface.send("Welcome to Ubuntu 16.04.7 LTS (GNU/Linux 4.15.0-142-generic i686)\r\n\r\n* Documentation:  https://help.ubuntu.com\r\n* Management: https://landscape.canonical.com\r\n* Support: https://ubuntu.com/advantage\n\r\n")
            attackInterface.send("UA Infra: Extended Security Maintenance (ESM) is not enabled.\r\n\r\n0 updates can be applied immediately.\r\n\r\n160 additional security updates can be applied with UA Infra: ESM\r\nLearn more about enabling UA Infra: ESM service for Ubuntu 16.04 at\r\nhttps://ubuntu.com/16-04")
            attackInterface.send("\r\nUbuntu comes with ABSOLUTELY NO WARRANTY, to the extent permitted by\r\napplicable law.\r\n\r\nLast login: Sun Apr 10 12:45:40 2022 from 10.0.2.5\r\n")
            flag = True
            while flag:
                attackInterface.send("$ ")
                command = ""
                while not command.endswith("\r"):
                    transport = attackInterface.recv(1024)
                    attackInterface.send(transport)
                    command += transport.decode("utf-8")

                attackInterface.send("\r\n")
                command = command.rstrip()
                log.write("$ " + command + "\n")
                print(command)
                if command == "exit":
                    flag = False
                else:
                    Response(command, attackInterface)

        except Exception as err:
            print('!!! Exception: {}: {}'.format(err._class_, err))
            traceback.print_exc()
            try:
                transport.close()
            except Exception:
                pass

        attackInterface.close()

    except Exception as err:
        print('!!! Exception: {}: {}'.format(err._class_, err))
        traceback.print_exc()
        try:
            transport.close()
        except:
            pass


def start_server(port, bind):
    """Init and run the ssh server"""
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        sock.bind((bind, port))
    except Exception as err:
        print('*** Bind failed: {}'.format(err))
        traceback.print_exc()
        sys.exit(1)

    threads = []
    while True:
        try:
            sock.listen(100)
            print('Listening for connection ...')
            client, addr = sock.accept()
        except Exception as err:
            print('*** Listen/accept failed: {}'.format(err))
            traceback.print_exc()
        new_thread = threading.Thread(target=SSHConnection, args=(client, addr))
        new_thread.start()
        threads.append(new_thread)

    for thread in threads:
        thread.join()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Run a fake ssh server')
    parser.add_argument("--port", "-p", help="The port to bind the ssh server to (default 22)", default=22, type=int, action="store")
    parser.add_argument("--bind", "-b", help="The address to bind the ssh server to", default="", type=str, action="store")
    args = parser.parse_args()
    start_server(args.port, args.bind)