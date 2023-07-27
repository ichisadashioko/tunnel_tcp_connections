import socket
import socketserver
import threading
import os
import argparse
import time


destination_ip = '192.168.192.2'
destination_port = 1080


def read_and_forward_thread_function(
    read_socket: socket.socket,
    forward_socket: socket.socket,
):
    while True:
        bs = read_socket.recv(1024)
        if len(bs) == 0:
            break
        forward_socket.sendall(bs)


def handle_client(client_socket: socket.socket, address):
    tunnel_client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    tunnel_client_socket.connect((destination_ip, destination_port))

    thread1 = threading.Thread(target=read_and_forward_thread_function, args=(client_socket, tunnel_client_socket,))
    thread1.start()

    thread2 = threading.Thread(target=read_and_forward_thread_function, args=(tunnel_client_socket, client_socket, ))
    thread2.start()

    thread1.join()
    thread2.join()

    client_socket.close()
    tunnel_client_socket.close()


server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

port_number = 1080
server_socket.bind(('0.0.0.0', port_number))
print(time.time_ns(), f'Listening on port {port_number}')
server_socket.listen()

while True:
    print(time.time_ns(), 'Waiting for client to connect')
    client_socket, address = server_socket.accept()
    print(f'Accepted connection from {address}')
    client_thread = threading.Thread(target=handle_client, args=(client_socket, address))
    client_thread.start()
    ts = time.time_ns()
    # handle_client_thread_list.append({
    #     'thread': client_thread,
    #     'time_ns': ts,
    # })
