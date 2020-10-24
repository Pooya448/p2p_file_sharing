from SocketUtil import *
import threading
from PDU_factory import *
import socket
from struct import *
import os
import math
import time

buffer_size = 1024
download_buffer_size = 187

def initialize_upload_socket(tcp_port, host_ip):
    TCP_upload_socket = socket.socket(family=socket.AF_INET, type=socket.SOCK_STREAM)
    TCP_upload_socket.bind((host_ip, tcp_port))
    TCP_upload_socket.listen(5)
    return TCP_upload_socket

def upload_request_handler(tcp_port, host_ip):
    socket = initialize_upload_socket(tcp_port, host_ip)
    while True:
        connection, address = socket.accept()
        upload_thread = threading.Thread(target=receive_upload_request, args=(connection,))
        upload_thread.run()

def receive_upload_request(socket):
    recieved_pdu = receive_pdu(socket)
    recieved_pdu_type = recieved_pdu.t
    if recieved_pdu_type == 'D':
        file = recieved_pdu.data
        if upload_file(socket, file):
            return
    else:
        response_pdu = create_EPDU(Error.DownloadRequestOnly)
        send_pdu(response_pdu, socket)

def get_chunk_num(filename):
    st = os.stat(filename)
    size = st.st_size
    num_pdu = math.ceil(float(size/100))
    return num_pdu

def check_for_ack(socket):
    ack_pdu = receive_pdu(socket)
    if ack_pdu.t != 'A':
        return False
    return True

def upload_file(socket, filename):
    with open(filename, 'rb') as file:
        num_pdu = get_chunk_num(filename)

        bytes_to_send = pack('d', num_pdu)
        socket.sendall(bytes_to_send)

        if not check_for_ack(socket):
            socket.close()
            return

        counter = 0
        bytes100 = bytes()
        byte = file.read(1)
        while byte:
            counter += 1
            bytes100 += byte
            byte = file.read(1)

            if counter == 99:
                response_pdu = create_FPDU(bytes100)
                send_pdu(response_pdu, socket)

                if not check_for_ack(socket):
                    socket.close()
                    return

                counter = 0
                bytes100 = bytes()

    response_pdu = create_LPDU(bytes100)
    send_pdu(response_pdu, socket)
    return True
