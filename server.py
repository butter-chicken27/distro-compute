import socket
import numpy as np
import queue
import pickle
import threading

DISTRIBUTION_PORT = 1556
MAIN_PORT = 1235
CLIENT_CONN_TYPE = 0
HELPER_CONN_TYPE = 1

work_queue = queue.Queue()
result_queue = queue.Queue()

def aggregate_results(opcode, results):
    if opcode == 'MAX':
        return np.max(results)
    elif opcode == 'SUM':
        return np.sum(results)
    elif opcode == 'SORT':
        final_array = []
        num_arrays = len(results)
        indices = [0 for _ in range(num_arrays)]
        count = 0
        while count < num_arrays:
            index = -1
            minimum = np.inf
            for i in num_arrays:
                if indices[i] == len(results[i]):
                    continue
                if results[i][indices[i]] < minimum:
                    index = i
                    minimum = results[i][indices[i]]
            final_array.append(minimum)
            indices[index] += 1
            if indices[index] == len(results[index]):
                count += 1
        return final_array
    else:
        raise NotImplementedError

def distribution_thread():
    print(f'Work Distribution Thread running on port {DISTRIBUTION_PORT}...')
    distribution_socket = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
    distribution_socket.bind(('localhost',DISTRIBUTION_PORT))
    distribution_socket.listen(100)
    distribution_socket.settimeout(0.001)
    connections = []
    while True:
        try:
            conn, _ = distribution_socket.accept()
            connections.append(conn)
        except socket.timeout:
            pass
        if(not work_queue.empty()):
            (client_addr,opcode,data) = work_queue.get()
            number_of_helpers = len(connections)
            data_length = data.shape[0]
            for i in range(number_of_helpers):
                if i == number_of_helpers - 1:
                    data_fragment = data[int(data_length * i / number_of_helpers):]
                else:
                    data_fragment = data[int(data_length * i / number_of_helpers): int(data_length * (i + 1) / number_of_helpers)]
                message = (opcode,data_fragment)
                connections[i].send(pickle.dumps(message))
            results = []
            for i in range(number_of_helpers):
                result = pickle.loads(connections[i].recv(4096))
                results.append(result)
            aggregated_result = aggregate_results(opcode,results)
            result_queue.put((client_addr, aggregated_result))


        

def main_thread():
    print(f'Main Thread running on port {MAIN_PORT}...')
    main_socket = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
    main_socket.bind(('localhost',MAIN_PORT))
    main_socket.listen(20)
    main_socket.settimeout(0.001)
    client_conns  = {}
    distro_thread = threading.Thread(target=distribution_thread)
    distro_thread.start()
    while True:
        if(not result_queue.empty()):
            (out_addr,result) = result_queue.get()
            client_conns[out_addr].send(pickle.dumps(result))
            client_conns[out_addr].close()
            del client_conns[out_addr]
        try:
            conn, addr = main_socket.accept()
            conn_type = int(conn.recv(1024).decode())
            if conn_type == HELPER_CONN_TYPE:
                conn.send(str(DISTRIBUTION_PORT).encode())
                conn.close()
            else:
                client_input = conn.recv(4096)
                (opcode,data) = pickle.loads(client_input)
                client_conns[addr] = conn
                work_queue.put((addr,opcode,data))
        except socket.timeout:
            continue

if __name__ == '__main__':
    main_thread()