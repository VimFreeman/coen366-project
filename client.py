#!/bin/python

import sys
import socket
import time

def main(args):
    # parse cli arguments
    (conn, ip, port, debug) = parse_cli(args)

    # create correct type of socket
    sock = socket.socket(socket.AF_INET, conn)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    # attempt to connect to server if TCP
    if conn == socket.SOCK_STREAM:
        status = sock.connect_ex((ip, port))
        while (status != 0):
            print ("TCP connection failed.. retrying in 1 second.")
            time.sleep(1)
        print ("TCP connection established")
    else:
        print ("Using UDP, no connection required")


# connect to server using tcp/udp ip and port and set debug flag

# start cli and wait for input

# parse input

# switch case
    # put
        # 000
        # filename length (5bits)
        # filename
        # file size (4 bytes)
        # file data

    # get
        # 001
        # Filename length (5bits)
        # filename

    # change
        # 010
        # old filename length (5bits)
        # old filename
        # new filename length (5bits)
        # new filename

    # help
        # 011
        # 5 bits unused

    # bye >> disconnect and exit

# listen for response

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
        sys.exit("Missing arguments. Usage: client.py [tcp/udp] [ip] [port] [0/1](debug)")
    main(sys.argv)
