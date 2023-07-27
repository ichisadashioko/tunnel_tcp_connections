import os
import time
import io
import struct
import socket
import argparse
import threading
import traceback

# %%


def read_and_forward_thread_function(
    read_socket: socket.socket,
    forward_socket: socket.socket,
):
    while True:
        try:
            if os.path.exists('stop'):
                break

            bs = read_socket.recv(1024)
            if len(bs) == 0:
                break
            forward_socket.sendall(bs)
        except Exception as ex:
            stacktrace = traceback.format_exc()
            print(ex, flush=True)
            print(stacktrace, flush=True)
            break

# def handle_client(client_socket: socket.socket, address):


def handle_client(input_dict: dict):
    try:
        client_socket = input_dict['client_socket']
        try:
            address = input_dict['address']
            destination_ip = input_dict['destination_ip']
            destination_port = input_dict['destination_port']

            tunnel_client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            tunnel_client_socket.connect((destination_ip, destination_port))

            try:
                thread1 = threading.Thread(target=read_and_forward_thread_function, args=(client_socket, tunnel_client_socket,))
                thread1.start()

                thread2 = threading.Thread(target=read_and_forward_thread_function, args=(tunnel_client_socket, client_socket, ))
                thread2.start()

                thread1.join()
                thread2.join()
            except Exception as ex:
                stacktrace = traceback.format_exc()
                print(ex, flush=True)
                print(stacktrace, flush=True)

            tunnel_client_socket.close()
        except Exception as ex:
            stacktrace = traceback.format_exc()
            print(ex, flush=True)
            print(stacktrace, flush=True)
        client_socket.close()
    except Exception as ex:
        stacktrace = traceback.format_exc()
        print(ex, flush=True)
        print(stacktrace, flush=True)


# %%
parser = argparse.ArgumentParser()
parser.add_argument('local_port', type=int)
parser.add_argument('remote_ip', type=str)
parser.add_argument('remote_port', type=int)
parser.add_argument('local_ipv4', type=str, default='0.0.0.0', nargs='?')

args = parser.parse_args()
print('args', args)

local_ipv4_str = args.local_ipv4
local_port = args.local_port
destination_ip = args.remote_ip
destination_port = args.remote_port

server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

server_socket.bind((local_ipv4_str, local_port))
print(time.time_ns(), f'Listening on  {local_ipv4_str}:{local_port}')
server_socket.listen()

while True:
    if os.path.exists('stop'):
        break

    print(time.time_ns(), 'Waiting for client to connect')
    client_socket, address = server_socket.accept()
    print(f'Accepted connection from {address}')
    input_dict = {
        'client_socket': client_socket,
        'address': address,
        'destination_ip': destination_ip,
        'destination_port': destination_port,
    }

    client_thread = threading.Thread(target=handle_client, args=(input_dict, ))
    client_thread.start()
    # ts = time.time_ns()
    # handle_client_thread_list.append({
    #     'thread': client_thread,
    #     'time_ns': ts,
    # })

'''
py tunnel_tcp_connections.py 20001 192.168.0.11 10001
'''
