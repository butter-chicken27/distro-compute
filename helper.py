import socket 
import random
import math
import threading
import time
import sys
import pickle
import numpy as np

ADDR_SIZE = 1024
ARR_SIZE = 100

# Create a TCP/IP socket
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# Connect the socket to the port where the server is listening
server_address = ('localhost', 10000) # edit server address here
print('connecting to %s port %s' % server_address)
sock.connect(server_address)

try:
    # Send data
    # message = 'This is the message.  It will be repeated.'
    # success message
    message = 1
    print('sending "%s"' % message)
    sock.sendall(message)

    # Receive the worker distribution thread address
    dist_address = sock.recv(ADDR_SIZE)
    print('received "%s"' % dist_address)

finally:
    print('closing socket')
    sock.close()


# connect to the distributer thread
# Connect the socket to the port where the server is listening
print('connecting to %s port %s' % dist_address)
sock.connect(dist_address)

try:
    amount_received = 0
    amount_expected = ARR_SIZE
    response_message = None
    
    while amount_received < amount_expected:
        # Receive array
        data = sock.recv(ARR_SIZE)
        (opcode, array) = pickle.loads(data)
        amount_received += len(array)
        
        print('received "%s"' % array)
        
        # Send response (currently max of received array)
        if opcode == "MAX":
            response_message = np.amax(array)
        # success message
        print('sending "%s"' % response_message)
        sock.sendall(response_message)

finally:
    print('closing socket')
    sock.close()