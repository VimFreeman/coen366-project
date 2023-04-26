#!/bin/python

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
