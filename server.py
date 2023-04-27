import sys
import socket
import os

BUFFER_SIZE = 4096

def main(args):
    (conn,ip,port,debug) = parse_cli(args)
# Start server using TCP/UDP, IP and port with debug flag.
    input("Press Enter to close the window...")

################################# TCP MODE ##################################################################
    # Start server using TCP/UDP, IP and port with debug flag.
    if conn == socket.SOCK_STREAM:
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_socket.bind((ip, port))
        server_socket.listen(1)  # Listen for 1 connection.
        print(f'TCP server listening on {ip}:{port}')
        
        while True:
            client_socket, client_address = server_socket.accept()
            data = client_socket.recv(BUFFER_SIZE)
            print(f"TCP connection established with {client_address}")
            handle_request(client_socket, client_address, data)

    else:
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        server_socket.bind((ip, port))
        print(f'UDP server listening on {ip}:{port}')

        while True:
            data, client_address = server_socket.recvfrom(BUFFER_SIZE)  
            print(f"UDP packet received from {client_address}")
            handle_request(server_socket, client_address, data)

def handle_request(sock, client_address, data):
    opcode = (data[0] & 0b11100000)>>5

    # PUT request.
    if opcode == 0:
        filename_length = data[0] & 0b00011111
        filename = data[1:filename_length+1].decode()
        file_size = int.from_bytes(data[filename_length+1:filename_length+5], byteorder='big')
        file_data = data[filename_length+5:]
        
        print(f'Received PUT request from {client_address}: {filename} ({file_size} bytes)')
        
        # Check if the file exists.
        with open(filename, 'wb') as f:
            f.write(file_data)
        print(f'{filename} saved successfully')
        response = bytearray(1)
        response[0] = 0b00000000  # Set response code to 000.

    # GET request.
    elif opcode == 1: 
        filename_length = data[0] & 0b00011111
        filename = data[1:filename_length+1].decode()

        if os.path.exists(filename):
            with open(filename, 'rb') as f:
                file_data = f.read()
                file_size = len(file_data).to_bytes(4, byteorder='big')
                print(f'Sending {filename} ({file_size} bytes) to {client_address}')
                response = bytearray()
                response = data  # 001 response is same as request opcode for correct GET request.
                response.extend(file_size)
                response.extend(file_data)
        else:
            response = bytearray(1)
            response[0] = 0b01000000  # Set response code to 010 Error-File Not Found.

    # CHANGE request.
    ################################ CHANGE REQUEST #################################################################
    elif opcode == 2:
        #change operation
        old_filename_length = data[0] & 0b00011111
        old_filename = data[1:old_filename_length+1].decode()
        new_filename_length = (data[old_filename_length+1] & 0b00011111)
        new_filename = data[old_filename_length+2:old_filename_length+new_filename_length+2].decode()
        
        response = bytearray(1)
        if os.path.isfile(old_filename):
            os.rename(old_filename, new_filename)
            response[0]  = 0b00000000
            print(f'Received CHANGE request from {client_address}: {old_filename} -> {new_filename}')
        else:
            print(f'{old_filename} file not found')
            response[0] = 0b10100000

    ################################ HELP REQUEST #################################################################
    elif opcode == 3:
        #help
        help_string = "skill issue detected, Proposition: Git Gud."
        help_len = len(help_string) & 0b00011111 #get filesize using 5 bits
        encoded_help_len = help_len.to_bytes(1, byteorder='big') #fit into 1 byte

        response = bytearray()
        response.append(0b11000000 | encoded_help_len) #110 HELP response
        response.extend(help_string.encode())
    ################################ UNKNOWN REQUEST #################################################################
    else:
        #unkn
        response = bytearray(1)
        response[0] = 0b11000000

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


if __name__ == "__main__":
    if len(sys.argv) < 5: 
        sys.exit("Missing arguments. Usage: 'client.py [tcp/udp] [ip] [port] [0/1](debug)'")
        print(sys.argv)
    main(sys.argv)
