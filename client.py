#!/bin/python

import os
import sys
import socket
import time

BUFFER_SIZE = 4096 # send or receive 4096 bytes at a time.

sock = socket.socket() # might cause problems?

def main(args):
    # parse cli arguments
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
                put(command)
            case "get":
                get(command)
            case "change":
                change(command)
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
            response = bytearray()
            response.append(0b000 << 5 | filename_length)  # 000 opcode for put request
            response.extend(filename.encode())
            response.extend(file_size_encoded)
            response.extend(file_data)
    else:
        print ("File does not exist.")
        return

    send(response)
    listen()
    return
    # 000
    # filename length (5bits)
    # filename
    # file size (4 bytes)
    # file data


def get(command):

    # call listen
    return
    # 001
    # Filename length (5bits)
    # filename


def change(command):
    # call listen
    return
    # 010
    # old filename length (5bits)
    # old filename
    # new filename length (5bits)
    # new filename


def help():
    # call listen
    return
    # 011
    # 5 bits unused


def bye():
    global sock
    if sock.proto == socket.SOCK_STREAM:
        sock.shutdown(socket.SHUT_RD)
        sys.exit("Connection closed and program terminated")    
    else:
        sys.exit("Nothing to close, program terminated.")

def listen():
    data = sock.recv(BUFFER_SIZE)
    opcode = (data[0] & 0b11100000) >> 5

    match opcode:
        case 000:

        case 001:

        case 010:

        case 011:

        case 101:

        case 110:
        
        case _:
# switch case
    # 000xxxxx >> correct put or change request

    # 001
    # filename length (5bits)
    # filename
    # file size (4bytes)
    # file data

    # 010xxxxx >> error - file not found

    # 011xxxxx >> error - unknown request

    # 101xxxxx >> error - unsuccessful change

    # 110
    # length data (5bits)
    # help data
    return

# sends data in 4kB chunks
def send(data):
    bytes_sent = 0;
    bytes_to_send = len(data)

    while bytes_sent <= bytes_to_send:
        payload = data[bytes_sent:bytes_sent+BUFFER_SIZE]
        bytes_sent += BUFFER_SIZE
        sock.sendall(payload)

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
