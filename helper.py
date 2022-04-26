import socket 
import random
import math
import threading
import time
import sys

ADDR_SIZE = 1024
ARR_SIZE = 100

# Create a TCP/IP socket
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# Connect the socket to the port where the server is listening
server_address = ('localhost', 10000) # edit server address here
print >> sys.stderr, 'connecting to %s port %s' % server_address
sock.connect(server_address)

try:
    # Send data
    # message = 'This is the message.  It will be repeated.'
    # success message
    message = 1
    print >> sys.stderr, 'sending "%s"' % message
    sock.sendall(message)

    # Receive the worker distribution thread address
    dist_address = sock.recv(ADDR_SIZE)
    print >> sys.stderr, 'received "%s"' % dist_address

finally:
    print >> sys.stderr, 'closing socket'
    sock.close()


# connect to the distributer thread
# Connect the socket to the port where the server is listening
print >> sys.stderr, 'connecting to %s port %s' % dist_address
sock.connect(dist_address)

try:
    
    amount_received = 0
    amount_expected = ARR_SIZE
    response_message = None
    
    while amount_received < amount_expected:
        # Receive array
        data = sock.recv(ARR_SIZE)
        amount_received += len(data)
        
        print >> sys.stderr, 'received "%s"' % data
        
        # Send response (currently max of received array)
        # success message
        response_message = max(data)
        print >> sys.stderr, 'sending "%s"' % response_message
        sock.sendall(response_message)

finally:
    print >> sys.stderr, 'closing socket'
    sock.close()