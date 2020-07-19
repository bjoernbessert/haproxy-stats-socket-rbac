#!/usr/bin/python3 -u

import argparse
import os
import pwd
import re
import socket
import struct
import sys
import yaml

SO_PEERCRED = 17


def getArgs():
    parser = argparse.ArgumentParser(description='', usage="usage: prog [options]")
    parser.add_argument('--destination_socket', action='store', dest='destination_socket', help='', required=True)
    parser.add_argument('--server_socket', action='store', dest='server_socket', help='', required=True)

    return parser.parse_args()


def send_command(destination_socket, command):

    client = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
    client.settimeout(10)

    try:
      client.connect(destination_socket)
    except socket.error:
      print("Cant connect to socket")
      sys.exit(1)

    client.sendall(command)

    result = b''
    buf = b''
    buf = client.recv(1024)

    while buf:
        result += buf
        buf = client.recv(1024)

    client.close()

    return result


def lookup_user(connection):
    creds = connection.getsockopt(socket.SOL_SOCKET, SO_PEERCRED, struct.calcsize('3i'))
    pid, uid, gid = struct.unpack("3i", creds)
    print("pid: %d, uid: %d, gid %d" % (pid, uid, gid))

    return pwd.getpwuid(uid).pw_name


def load_permissions():
    # abspath not working if script is called via symlink
    #fileDir = os.path.dirname(os.path.abspath(__file__))
    fileDir = os.path.dirname(os.path.realpath(__file__))
    configfile = 'permissions.yml'
    configfile_abs_path = os.path.join(fileDir, configfile)
    f = open(configfile_abs_path)
    permissions = yaml.load(f)
    f.close()

    return permissions


def has_permission(username, command):
    perms = load_permissions()

    if username in perms['permissions'].keys():
        for regex in perms['permissions'][username]:
            matched = re.search(regex, command.decode('utf-8'), re.IGNORECASE)
            if matched:
                print("Access granted!")
                return True
    else:
        return False

    # secure default
    return False


def check_preconditions(destination_socket, server_socket):

    if not os.path.exists(destination_socket):

        #TODO: if param is set then warning only
        print("Error: Destination_socket %s doesnt exist" % destination_socket)
        sys.exit(1)

    try:
        client = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        client.settimeout(10)
        client.connect(destination_socket)
        client.close()
    except socket.error:
        #TODO: if param is set then warning only
        print("Error: Cant connect to socket on startup")
        sys.exit(1)

    try:
        os.unlink(server_socket)
    except OSError:
        if os.path.exists(server_socket):
            raise


def server_loop(destination_socket, server_socket):

    sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
    print("Starting up on %s" % server_socket)
    sock.bind(server_socket)
    os.chmod(server_socket, 0o666)
    sock.listen(10)

    while True:
        print("Waiting for a connection")
        try:
            connection, client_address = sock.accept()
        except KeyboardInterrupt:
            print("Catching KeyboardInterrupt")
            break

        try:
            print("New connection from client")
            while True:

                username = lookup_user(connection)
                print("Username:", username)

                data = connection.recv(1024)

                print('Received "%s"' % data)
                if data:
                    if not has_permission(username, data):
                        connection.sendall(bytes('Permission Denied for this command', 'UTF-8'))
                        print("Permission Denied for this command")
                        break

                    returndata = send_command(destination_socket, data)

                    print("Sending data back to the client")
                    connection.sendall(returndata)
                    connection.shutdown(socket.SHUT_RDWR)
                else:
                    print("No more data from client")
                    break
        finally:
            print("Closing and shutdown connection")
            connection.shutdown(socket.SHUT_RDWR)
            connection.close()

    print("Shutting down...")
    sock.close()
    os.remove(server_socket)
    print("Done")


def main():

    args_parsed = getArgs()

    destination_socket = args_parsed.destination_socket
    server_socket = args_parsed.server_socket

    check_preconditions(destination_socket, server_socket)

    server_loop(destination_socket, server_socket)


if __name__ == '__main__':
    main()
