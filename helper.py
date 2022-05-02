import socket 
import pickle
import numpy as np
from server import HELPER_CONN_TYPE, MAIN_PORT

SERVER_IP = 'localhost'

# Create a TCP/IP socket
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# Connect the socket to the port where the server is listening
server_address = (SERVER_IP, MAIN_PORT) # edit server address here
sock.connect(server_address)

try:
    message = HELPER_CONN_TYPE
    sock.sendall(str(message).encode())
    # Receive the worker distribution thread port number
    DIST_PORT_NUMBER = int(sock.recv(4096).decode())
finally:
    sock.close()

# connect to the work distribution thread
# Connect the socket to the port where the server is listening
distribution_thread_address = (SERVER_IP,DIST_PORT_NUMBER)
sock = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
sock.connect(distribution_thread_address)
sock.settimeout(0.01)
print('Connected to Work Distribution Server and listening for operations...')

while True:
    try:
        # Receive array
        data = sock.recv(4096)
        (opcode, array) = pickle.loads(data)
        
        # Send response (currently max of received array)
        if opcode == "MAX":
            response_message = np.amax(array)
        elif opcode == "SUM":
            response_message = np.sum(array)
        elif opcode == "SORT":
            response_message = np.sort(array)
        sock.sendall(pickle.dumps(response_message))
    except socket.timeout:
        continue