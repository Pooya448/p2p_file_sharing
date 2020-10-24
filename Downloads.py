from SocketUtil import *
import socket
import threading
from PDU_factory import *
from struct import *
import os
import math
import time
from progress import *

buffer_size = 1024
download_buffer_size = 187

def initialize_download_socket():
    TCP_download_socket = socket.socket(family=socket.AF_INET, type=socket.SOCK_STREAM)
    return TCP_download_socket

def request_download(filename, socket, ip, port):
    request_pdu = create_DPDU(filename)
    socket.connect((ip, port))
    send_pdu(request_pdu, socket)
    return

def download_next_chunk(socket):
    recieved_bytes = socket.recv(download_buffer_size)
    recieved_pdu = binary_to_pdu(recieved_bytes)
    return recieved_pdu

def download_file(filename, ip, port):
    socket = initialize_download_socket()
    request_download(filename, socket, ip, port)

    num_iter = recieve_file_size(socket)
    send_ack(socket)

    cur_iter = 0
    last_pdu_type = ''
    chunks = []

    while last_pdu_type != 'L':
        recieved_pdu = download_next_chunk(socket)
        send_ack(socket)

        chunks.append(recieved_pdu.data)
        last_pdu_type = recieved_pdu.t

        cur_iter += 1
        show_progress(cur_iter, num_iter)

    show_progress(100, 100)
    print("\n")
    socket.close()
    if save_file(chunks, filename):
        return True
    return False


def save_file(chunks, filename):
    with open(filename, 'wb') as file:
        for chunk in chunks:
            file.write(chunk)
        return True

def send_ack(socket):
    ack_pdu = create_APDU('Meh')
    send_pdu(ack_pdu, socket)
    return

def recieve_file_size(socket):
    file_size = socket.recv(41)
    num_iter = unpack('d', file_size)[0]
    return num_iter
