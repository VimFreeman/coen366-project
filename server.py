#!/bin/python
import sys
import socket

def main(args)
    (conn,ip,port,debug) = parse_cli(args)
#start sever using tcp/udp ip and port with debug flag

if conn == 1
    server = socket
else
#wait for client connection

#parse input

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
    # bye >> disconnect and wait for new client

   
    
def parse_cli(args):
    # parse connection type
    conn = args[1]
    if conn.lower() == "udp": conn = 0
    elif conn.lower() == "tcp": conn = 1
    else: sys.exit("Error: Invalid connection type")

    # parse ip
    ip = args[2]
    temp = ip.split('.')
    if len(temp) < 4: sys.exit("Error: Invalid IP address")
    for num in temp:
        if int(num) < 0 or int(num) > 255:
            sys.exit("Error: Invalid IP address")

    # parse port
    port = args[3]
    if int(port) < 0 or int(port) > 65535:
        sys.exit("Error: Invalid port number")

    # parse debug
    debug = args[4]
    if debug == 1: debug = True
    else: debug = False

    return (conn, ip, port, debug)

def main():
    print("[sever starting]")
    server = socket.socket(socket.AF_)
