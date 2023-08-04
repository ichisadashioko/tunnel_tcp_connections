import os
import socket
import io
import time
import argparse

parser = argparse.ArgumentParser()
parser.add_argument('ipv4', nargs='?', type=str, default='127.0.0.1')
parser.add_argument('port', nargs='?', type=int, default=20001)
args = parser.parse_args()

print('args', args)

ipv4_str = args.ipv4
destination_port = args.port

socket_obj = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
# socket_obj.bind((ipv4_str, destination_port))
socket_obj.settimeout(5)
socket_obj.connect((ipv4_str, destination_port))
send_byte_count = socket_obj.send(b'stop')
print(f'send_byte_count {send_byte_count}')
print('wait 1 secs')
time.sleep(1)
socket_obj.close()
