import os
import time
import io
import struct
import socket
import argparse
import threading
import traceback

# %%
RS = '\033[0m'
R = '\033[91m'
G = '\033[92m'
Y = '\033[93m'
# %%
GLOBAL_STOP_FLAG = False


def read_and_forward_thread_function(
    read_socket: socket.socket,
    forward_socket: socket.socket,
):
    global GLOBAL_STOP_FLAG
    try:
        if os.path.exists('stop'):
            return

        if os.path.exists(stop_filepath):
            GLOBAL_STOP_FLAG = True
            return

        if GLOBAL_STOP_FLAG:
            return

        bs = read_socket.recv(1024)
        if len(bs) == 0:
            return

        if len(bs) >= 4:
            if bs[0:4] == b'stop':
                print('stop command received', flush=True)
                GLOBAL_STOP_FLAG = True
                return

        forward_socket.sendall(bs)
    except Exception as ex:
        stacktrace = traceback.format_exc()
        print(ex, flush=True)
        print(stacktrace, flush=True)

    while True:
        try:
            if os.path.exists('stop'):
                break

            if os.path.exists(stop_filepath):
                GLOBAL_STOP_FLAG = True
                break

            if GLOBAL_STOP_FLAG:
                break

            # TODO split into 2 threads
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

            tunnel_client_socket = None
            try:
                tunnel_client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                tunnel_client_socket.settimeout(5)
                tunnel_client_socket.connect((destination_ip, destination_port))
                # put back to default blocking behavior - TODO
                tunnel_client_socket.settimeout(None)
            except Exception as ex:
                stacktrace = traceback.format_exc()
                print(f'{Y}{ex}{RS}', flush=True)
                print(f'{R}{stacktrace}{RS}', flush=True)
                print(f'{Y}failed to connect to tunnel destination{RS} - {R}{destination_ip}{RS}:{G}{destination_port}{RS}', flush=True)

                tunnel_client_socket = None

            if tunnel_client_socket is not None:
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

stop_filepath = f'stop_{local_port}'
if os.path.exists(stop_filepath):
    os.remove(stop_filepath)

server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

server_socket.bind((local_ipv4_str, local_port))
print(time.time_ns(), f'Listening on  {local_ipv4_str}:{local_port}')
server_socket.listen()

# instance_prefix = f'{local_ipv4_str}:{local_port} -> {destination_ip}:{destination_port}'
instance_prefix = f'{R}{local_ipv4_str}:{local_port}{RS} -> {G}{destination_ip}:{destination_port}{RS}'

accepted_connection_count = 0

while True:
    try:
        if os.path.exists('stop'):
            break

        if os.path.exists(stop_filepath):
            GLOBAL_STOP_FLAG = True
            break

        if GLOBAL_STOP_FLAG:
            break

        print(time.time_ns(), instance_prefix, f'accepted_connection_count {G}{accepted_connection_count}{RS}')
        print(f'create {R}{stop_filepath}{RS} to stop the tunnel')
        client_socket, address = server_socket.accept()
        accepted_connection_count += 1
        print(f'Accepted connection from {address}')
        input_dict = {
            'client_socket': client_socket,
            'address': address,
            'destination_ip': destination_ip,
            'destination_port': destination_port,
        }

        client_thread = threading.Thread(target=handle_client, args=(input_dict, ))
        client_thread.start()
    except Exception as ex:
        stacktrace = traceback.format_exc()
        print(ex, flush=True)
        print(stacktrace, flush=True)
        GLOBAL_STOP_FLAG = True
        break

    # ts = time.time_ns()
    # handle_client_thread_list.append({
    #     'thread': client_thread,
    #     'time_ns': ts,
    # })

print(time.time_ns(), f'main thread finished', flush=True)
