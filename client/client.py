#!/bin/python

import os
import sys
import socket
import time

BUFFER_SIZE = 4096 # send or receive 4096 bytes at a time.

sock = socket.socket() # might cause problems?
ip = 0
port = 0

def main(args):
    # parse cli arguments
    global ip, port
    (conn, ip, port, debug) = parse_cli(args)

    # create correct type of socket
    global sock
    sock = socket.socket(socket.AF_INET, conn)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    # attempt to connect to server if TCP
    if conn == socket.SOCK_STREAM:
        status = sock.connect_ex((ip, port))
        while (status != 0):
            print ("TCP connection failed.. retrying in 1 second.")
            time.sleep(1)
            status = sock.connect_ex((ip, port))
        print (f"TCP connection established with {ip}:{port}")
    else:
        print ("Using UDP, no connection required")

    # connection is good, now we prompt the user for commands until "bye"
    while(True):
        command = input("myFTP>")
        command = command.split(" ")

        # parse first argument and call respective function
        match(command[0]): 
            case "":
                continue
            case "help":
                help()
            case "put":
                put(command,)
            case "get":
                get(command,)
            case "change":
                change(command,)
            case "bye":
                bye()
            case _:
                print("Uknown command")
                continue

def put(command):
    filename = command[1]
    filename_length = len(filename) 
    if filename_length > 31:
        print("Filename too long. Maximum 31 characters")
        return
    
    if os.path.exists(filename):
        with open(filename, 'rb') as f:
            file_data = f.read()
            file_size = os.path.getsize(filename)
            file_size_encoded = file_size.to_bytes(4, byteorder="big")
            request = bytearray()
            request.append(0b000 << 5 | filename_length)  # 000 opcode for put request
            request.extend(filename.encode())
            request.extend(file_size_encoded)
            request.extend(file_data)
    else:
        print ("File does not exist.")
        return

    send(request)
    listen()
    return


def get(command):
    filename = command[1]
    filename_length = len(filename)
    request = bytearray()
    request.append(0b001 << 5 | filename_length)
    request.extend(filename.encode())
    
    send(request)
    listen()

    return


def change(command):
    old_filename = command[1]
    old_filename_length = len(old_filename)
    new_filename = command[2]
    new_filename_length = len(new_filename)
    request = bytearray()
    request.append(0b001 << 5 | old_filename_length)
    request.extend(old_filename.encode())
    request.append(0b000 << 5 | new_filename_length)
    request.extend(new_filename.encode())

    send(request)
    listen()
    return


def help():
    request = bytearray()
    request.append(0b01100000)

    send(request)
    listen()
    return


def bye():
    global sock
    if sock.type == socket.SOCK_STREAM:
        sock.shutdown(socket.SHUT_RD)
        sys.exit("Connection closed and program terminated")    
    else:
        sys.exit("Nothing to close, program terminated.")

def listen():
    data = sock.recv(BUFFER_SIZE)
    opcode = (data[0] & 0b11100000) >> 5

    match opcode:
        case 0: # Correct put/change request
            print("File uploaded/renamed successfully")

        case 1: # Get request response
            filename_length = data[0] & 0b11111
            filename = data[1:filename_length]
            file_size = int.from_bytes(data[filename_length:filename_length+4])
            file_data = data[filename_length+4::]

            with open(filename, 'wb') as f:
                f.write(file_data)

            remaining_bytes = file_size - (BUFFER_SIZE - len(file_data))
            while (remaining_bytes >= BUFFER_SIZE):
                data = sock.recv(BUFFER_SIZE)
                with open(filename, 'wb') as f:
                    f.write(file_data)
                remaining_bytes = remaining_bytes - BUFFER_SIZE

            data = sock.recv(remaining_bytes)
            with open(filename, 'wb') as f:
                f.write(file_data)

        case 2: # File not found
            print("Error: File not found")
        case 3: # Unknown request
            print("Error: Uknown request")
        case 5: # Unsuccessful change
            print("Error: Change request unsuccessful")
        case 6: # Help request response
            help_length = data[0] &0b11111
            help = data[1:help_length]
            print(help)
        case _: # default case
            print("Error: Server response unknown")

    return

# sends data in 4kB chunks
def send(data):
    global ip, port

    bytes_sent = 0;
    bytes_to_send = len(data)

    while bytes_sent < bytes_to_send:
        payload = data[bytes_sent:bytes_sent+BUFFER_SIZE]
        bytes_sent += BUFFER_SIZE
        sock.sendto(payload, (ip,port))

def parse_cli(args):
    # parse connection type
    conn = args[1]
    if conn.lower() == "udp": conn = socket.SOCK_DGRAM
    elif conn.lower() == "tcp": conn = socket.SOCK_STREAM
    else: sys.exit("Error: Invalid connection type")

    # parse ip
    ip = args[2]
    temp = ip.split('.')
    if len(temp) < 4: sys.exit("Error: Invalid IP address")
    for num in temp:
        if int(num) < 0 or int(num) > 255:
            sys.exit("Error: Invalid IP address")

    # parse port
    port = int(args[3])
    if port < 1 or port > 65535:
        sys.exit("Error: Invalid port number")

    # parse debug
    debug = args[4]
    if debug == 1: debug = True
    else: debug = False

    return (conn, ip, port, debug)


if __name__ == "__main__":
    if len(sys.argv) < 5: 
        sys.exit("Missing arguments. Usage: 'client.py [tcp/udp] [ip] [port] [0/1](debug)'")
    main(sys.argv)
