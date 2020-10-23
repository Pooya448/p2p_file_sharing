
import socket
import pickle
from PDU import PDU
from resources import resources
from message import Error, Success


## create UDP socket

local_ip = "127.0.0.1"
local_port = 8888
buffer_szie = 1024

server_welcome_message = "Fuck you client!"
wlc_message_bytes = str.encode(server_welcome_message)

UDP_server_socket = socket.socket(type=socket.SOCK_DGRAM, family=socket.AF_INET)
UDP_server_socket.bind((local_ip, local_port))

## create PDU

## this function converts recieved binary data to PDU
def binary_to_pdu (binary_pdu):
    return pickle.loads(binary_pdu)

def pdu_to_binary (pdu):
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
        # response_pdu = create_PDU(Type='A',data=Success.RegisterOK)
        return 'A', Success.RegisterOK

        # print('File: ', file, ' from host: ', client_address, ' successfully resgistered on server.')
    else:
        # response_pdu = create_PDU(Type='E',data=Error.RegisterFail)
        return 'E', Error.RegisterFail

        # print('File: ', file, ' from host: ', client_address, ' was already registered on the server.')


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
        print("******\n", entry, "\n*****")
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
        print("******\n", entry, "\n*****")
        response_type, response_data = delete_file(host_ip=ip, file_name=file)

        if response_type == 'A':
            print('File: ', file, ' from host: ', client_address, ' successfully removed from server.')

        if response_type == 'E':
            print('File: ', file, ' from host: ', client_address, ' was not found on the server.')

        response_pdu = create_PDU(Type=response_type,data=response_data)
        bytes_to_send = pdu_to_binary(response_pdu)
        UDP_server_socket.sendto(bytes_to_send, client_address)

    ## if the pair wants to know the address of a specific file
    elif pdu_type == 'S':
        pass

    ## if pair wants to know the list of all files available in the network
    elif pdu_type == 'O':
        pass
