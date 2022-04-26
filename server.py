from audioop import add
import pickle
from pydoc import cli
import socket
from textwrap import wrap
import numpy as np
import queue
import pickle

DISTRIBUTION_PORT = 1556
MAIN_PORT = 1235

work_queue = queue.Queue()
result_queue = queue.Queue()

main_socket = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
main_socket.bind(('localhost',MAIN_PORT))
main_socket.listen(20)
main_socket.settimeout(0.001)

client_conns  = {}

while True:
    if(not result_queue.empty()):
        (out_addr,result) = result_queue.get()
        client_conns[addr].send(str(result).encode())
        client_conns[addr].close()
        del client_conns[addr]
    
    try:
        conn, addr = main_socket.accept()
        conn_type = int(conn.recv(1024).decode())
        if conn_type == 0:
            conn.send(str(DISTRIBUTION_PORT).encode())
            conn.close()
        else:
            client_input = conn.recv(4096)
            (opcode,data) = pickle.loads(client_input)

            client_conns[addr] = conn
            work_queue.put((addr,opcode,data))
    except socket.timeout:
        continue