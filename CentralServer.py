
import socket
import pickle
from PDU import PDU
from resources import resources
from message import Error, Success
import random
# import sys


## create UDP socket

local_ip = "127.0.0.1"
local_port = 8888
buffer_szie = 1024

server_welcome_message = "Fuck you client!"
wlc_message_bytes = str.encode(server_welcome_message)

UDP_server_socket = socket.socket(type=socket.SOCK_DGRAM, family=socket.AF_INET)
UDP_server_socket.bind((local_ip, local_port))



def check_peer_exit(client_ip):
    flag = True
    for ip, _, _ in resources:
        if ip == client_ip:
            flag = False
    if flag:
        print("Host with address:", client_ip, "exited.")

## this function converts recieved binary data to PDU
def binary_to_pdu (binary_pdu):
    return pickle.loads(binary_pdu)

def pdu_to_binary (pdu):
    # print(sys.getsizeof(pdu))
    # binary = pickle.dumps(pdu)
    # print(sys.getsizeof(binary))
    return pickle.dumps(pdu)

def create_PDU(Type, data):
    return PDU(Type, data)

def delete_file(host_ip, file_name):

    for ip, port, file in resources:
        if ip == host_ip and file == file_name:
            entry_to_delete = (ip, port, file)
            resources.remove(entry_to_delete)
            return 'A', Success.DeleteOK
    return 'E', Error.FileNotFound

def register_file(entry):

    if entry not in resources:
        resources.append(entry)
        return 'A', Success.RegisterOK
    else:
        return 'E', Error.RegisterFail

def list_files():
    if any(resources):
        list_to_send = []
        for _, _, file in resources:
            list_to_send.append(file)
        list_to_send = list(set(list_to_send))
        return 'O', list_to_send
    else:
        return 'E', Error.ServerEmpty


def search_file(file_name):
    host_list = []
    for ip, port, file in resources:
        if file == file_name:
            host_list.append((ip, port))
    if any(host_list):
        return 'S', random.choice(host_list)
    return 'E', Error.FileNotFound

while True:

    print("\n*************************")
    print("UDP Serevr Listening...")

    ## Recieve messages from client (UDP socket)
    bytes_address_pair = UDP_server_socket.recvfrom(buffer_szie)
    client_message = bytes_address_pair[0]
    client_address = bytes_address_pair[1]

    print('Connected to host: ', client_address)
    ## convert recieved binary data to PDU
    extracted_pdu = binary_to_pdu(client_message)
    ##extract pdu_type
    pdu_type = extracted_pdu.t
    # print("******\n", pdu_type, "\n*****")
    ## if the pair wants to register file
    if pdu_type == 'R':

        ip, port, file = extracted_pdu.data
        entry = (ip, port, file)
        # print("******\n", entry, "\n*****")
        response_type, response_data = register_file(entry)

        if response_type == 'A':
            print('File: ', file, ' from host: ', client_address, ' successfully resgistered on server.')

        if response_type == 'E':
            print('File: ', file, ' from host: ', client_address, ' was already registered on the server.')

        response_pdu = create_PDU(Type=response_type,data=response_data)
        bytes_to_send = pdu_to_binary(response_pdu)
        UDP_server_socket.sendto(bytes_to_send, client_address)

    ## if the pait wants to remove a file
    elif pdu_type == 'U':

        file = extracted_pdu.data
        ip , port = client_address
        # print("******\n", entry, "\n*****")
        response_type, response_data = delete_file(host_ip=ip, file_name=file)

        if response_type == 'A':
            print('File: ', file, ' from host: ', client_address, ' successfully removed from server.')

        if response_type == 'E':
            print('File: ', file, ' from host: ', client_address, ' was not found on the server.')

        check_peer_exit(ip)

        response_pdu = create_PDU(Type=response_type,data=response_data)
        bytes_to_send = pdu_to_binary(response_pdu)
        UDP_server_socket.sendto(bytes_to_send, client_address)

    ## if the pair wants to know the address of a specific file
    elif pdu_type == 'S':
        file = extracted_pdu.data
        ip , port = client_address

        response_type, response_data = search_file(file_name=file)

        if response_type == 'S':
            print('File: ', file, ' for requesting host: ', client_address, ' successfully retrieved.')

        if response_type == 'E':
            print('File: ', file, ' for requesting host: ', client_address, ' was not found on the server.')

        response_pdu = create_PDU(Type=response_type,data=response_data)
        bytes_to_send = pdu_to_binary(response_pdu)
        UDP_server_socket.sendto(bytes_to_send, client_address)


    ## if pair wants to know the list of all files available in the network
    elif pdu_type == 'O':
        response_type, response_data = list_files()
        response_pdu = create_PDU(Type=response_type,data=response_data)
        # print("Size: ", sys.getsizeof(response_pdu))
        bytes_to_send = pdu_to_binary(response_pdu)
        UDP_server_socket.sendto(bytes_to_send, client_address)
