
import socket
import pickle
from message import Error, Success
from PDU_factory import *
import threading
import random
from Downloads import download_file
from Uploads import upload_request_handler

peer_registered_entries = []

server_address_port= ("127.0.0.1", 8888)
buffer_size = 1024
download_buffer_size = 187

TCP_PORT = random.randint(5000, 9000)

HOST_IP = "127.0.0.1"

UDP_peer_socket = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)

def send_pdu_to_server(bytes_to_send):
    bytes_to_send = pdu_to_binary(bytes_to_send)
    UDP_peer_socket.sendto(bytes_to_send, server_address_port)

def receive_server_pdu():
    server_response = UDP_peer_socket.recvfrom(buffer_size)[0]
    response_pdu = binary_to_pdu(server_response)
    return response_pdu

def binary_to_pdu (binary_pdu):
    return pickle.loads(binary_pdu)

def pdu_to_binary (pdu):
    return pickle.dumps(pdu)


def register_file(file):
    my_ip = str(socket.gethostbyname(socket.gethostname()))
    register_pdu = create_RPDU(ip=my_ip, port=TCP_PORT, file=file)

    send_pdu_to_server(register_pdu)
    response_pdu = receive_server_pdu()

    response_pdu_type = response_pdu.t
    if response_pdu_type == 'A':
        peer_registered_entries.append(file)
        print('Server Response:', response_pdu.data.value)
    elif response_pdu_type == 'E':
        print('Server Response:', response_pdu.data.value)

def retrieve_files():
    list_pdu = create_OPDU()

    send_pdu_to_server(list_pdu)
    response_pdu = receive_server_pdu()

    response_pdu_type = response_pdu.t

    if response_pdu_type == 'O':
        print("Files on server:")
        counter = 1
        for file in response_pdu.data:
            print(counter,".",file)
            counter += 1
        return True
    elif response_pdu_type == 'E':
        print('Server Response:', response_pdu.data.value)
        return False

def retrieve_file_address(file):
    list_pdu = create_SPDU(file)

    send_pdu_to_server(list_pdu)
    response_pdu = receive_server_pdu()

    if response_pdu.t == 'S':
        host_ip, host_port = response_pdu.data
        print('\nHost IP:', host_ip, "\tHost Port:", host_port)
        return host_ip, host_port
    elif response_pdu.t == 'E':
        print('Server Response:', response_pdu.data.value)


def remove_file(file):

    remove_pdu = create_UPDU(file=file)

    send_pdu_to_server(remove_pdu)
    response_pdu = receive_server_pdu()

    response_pdu_type = response_pdu.t
    if response_pdu_type == 'A':
        print('Server Response:', response_pdu.data.value)
        return True
    elif response_pdu_type == 'E':
        print('Server Response:', response_pdu.data.value)
        return False

def exit_peer():
    counter = 0
    files_removed = []
    for file in peer_registered_entries:
        if remove_file(file):
            files_removed.append(file)
            counter += 1
    if counter == len(peer_registered_entries):
        print("Successfully removed", counter, "entries from server")
        print("Files removed:")
        for file in files_removed:
            print(file)
        return True
    return False

TCP_Daemon = threading.Thread(target=upload_request_handler, args=(TCP_PORT, HOST_IP), daemon=True)
TCP_Daemon.start()

while True:

    print('*************\nInput Your command: ')
    command = input()
    if command == 'O':
        if retrieve_files():
            print("Wanna download? [n / y]")
            ans = input()
            if ans == 'y':
                print("Enter the name of file to download:")
                selected_file = input()
                if selected_file not in peer_registered_entries:
                    host_ip, host_port = retrieve_file_address(selected_file)
                    if download_file(selected_file, host_ip, host_port):
                        register_file(selected_file)
                else:
                    print("File already exist in local")

    elif command == 'L':
        if any(peer_registered_entries):
            print("Files registered on the central server:")
            for file in peer_registered_entries:
                print(file)
        else:
            print("There are no local files by now.")

    elif command == 'R':
        print("Enter file name to register:")
        file = input()
        register_file(file)

    if command == 'U':
        print("Enter file name to delete from server:")
        file = input()
        if remove_file(file):
            peer_registered_entries.remove(file)

    if command == 'E':
        if exit_peer():
            exit()
