#!/bin/python
import sys
import socket
import os

def main(args):
    (conn,ip,port,debug) = parse_cli(args)
# Start server using TCP/UDP, IP and port with debug flag.

################################# TCP MODE ##################################################################
    # Start server using TCP/UDP, IP and port with debug flag.
    if conn == socket.SOCK_STREAM:
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_socket.bind((ip, port))
        server_socket.listen(1)  # Listen for 1 connection.
        print(f'TCP server listening on {ip}:{port}')
        
        while True:
            client_socket, client_address = server_socket.accept()
            data = client_socket.recv(512)
            print(f"TCP connection established with {client_address}")
            handle_request(client_socket, client_address, data)

    else:
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        server_socket.bind((ip, port))
        print(f'UDP server listening on {ip}:{port}')

        while True:
            data, client_address = server_socket.recvfrom(512)  # 512 bytes max.
            print(f"UDP packet received from {client_address}")
            handle_request(server_socket, client_address, data)

def handle_request(sock, client_address, data):
    opcode = data[0] & 0b00000111

    # PUT request.
    if opcode == 0:
        filename_length = (data[0] & 0b11111000) >> 3
        filename = data[1:filename_length+1].decode()
        file_size = int.from_bytes(data[filename_length+1:filename_length+5], byteorder='big')
        file_data = data[filename_length+5:]
        
        print(f'Received PUT request from {client_address}: {filename} ({file_size} bytes)')
        
        # Check if the file exists.
        response = bytearray(1)
        if os.path.exists(filename):
            print(f'{filename} already exists')
            response[0] = 0b00000101  # 101 response for unsuccessful change.
        else:
            # Create new file and write data to it.
            with open(filename, 'wb') as f:
                f.write(file_data)
            print(f'{filename} saved successfully')
            response[0] = 0b00000000  # Set response code to 000.

    # GET request.
    elif opcode == 1: 
        filename_length = (data[0] & 0b11111000) >> 3
        filename = data[1:filename_length+1].decode()

        if os.path.exists(filename):
            with open(filename, 'rb') as f:
                file_data = f.read()
                file_size = len(file_data) & 0b11111  # Get file size using 5 bits.
                encoded_file_size = file_size.to_bytes(1, byteorder='big')  # Fit into 1 byte.
                print(f'Sending {filename} ({file_size} bytes) to {client_address}')
                response = bytearray()
                response.append(0b00000001 | (encoded_file_size<<3))  # 001 response for correct GET request.
                response.extend(filename.encode())
                response.extend(file_data)
        else:
            response = bytearray(1)
            response[0] = 0b00000010  # Set response code to 010 Error-File Not Found.

    # CHANGE request.
    ################################ CHANGE REQUEST #################################################################
    elif opcode == 2:
        #change operation
        old_filename_length = (data[0] & 0b11111000) >> 3
        old_filename = data[1:old_filename_length+1].decode()
        new_filename_length = (data[old_filename_length+1] & 0b11111000) >> 3
        new_filename = data[old_filename_length+2:old_filename_length+new_filename_length+2].decode()
        
        response = bytearray(1)
        if os.path.isfile(old_filename):
            os.rename(old_filename, new_filename)
            response[0]  = 0b00000000
            print(f'Received CHANGE request from {client_address}: {old_filename} -> {new_filename}')
        else:
            print(f'{old_filename} file not found')
            response[0] = 0b00000101

    ################################ HELP REQUEST #################################################################
    elif opcode == 3:
        #help
        help_string = "skill issue detected, Proposition: Git Gud."
        help_len = len(help_string) & 0b11111 #get filesize using 5 bits
        encoded_help_len = help_len.to_bytes(1, byteorder='big') #fit into 1 byte

        response = bytearray()
        response.append(0b00000110 | encoded_help_len<<3) #110 HELP response
        response.extend(help_string.encode())
    ################################ UNKNOWN REQUEST #################################################################
    else:
        #unkn
        response = bytearray(1)
        response[0] = 0b00000110

    ################################ SEND REQUEST #################################################################
    #send response

    sock.sendto(response,client_address)


   
def parse_cli(args):
    # parse connection type
    conn = args[1]
    if conn.lower() == "udp":
        conn = socket.SOCK_DGRAM
    elif conn.lower() == "tcp":
        conn = socket.SOCK_STREAM
    else:
        sys.exit("Error: Invalid connection type")

    # parse ip
    ip = args[2]

    # parse port
    port = int(args[3])

    # parse debug flag
    debug = False
    if len(args) == 5 and args[4].lower() == "debug":
        debug = True

    return (conn, ip, port, debug)

