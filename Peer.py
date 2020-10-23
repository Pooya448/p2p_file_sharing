
import socket
import select
import pickle
from PDU import PDU
from message import Error, Success

peer_registered_entries = []
## create UDP socket in order to connect to central server
# client_greet_message = "Fuck you server!"
# client_greet_message_bytes = str.encode(client_greet_message)

server_address_port= ("127.0.0.1", 8888)
buffer_size = 1024

TCP_Port = 7777
UDP_client_socket = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)
# UDP_client_socket.sendto(client_greet_message_bytes, server_address_port)

# msg_from_server = UDP_client_socket.recvfrom(buffer_size)

# msg = "Message from Server {}".format(msg_from_server[0])
# print(msg)
## create PDU


def send_pdu_to_server(pdu):
    bytes_to_send = pdu_to_binary(pdu)
    UDP_client_socket.sendto(bytes_to_send, server_address_port)

def receive_server_pdu():
    server_response = UDP_client_socket.recvfrom(buffer_size)[0]
    response_pdu = binary_to_pdu(server_response)
    return response_pdu

def binary_to_pdu (binary_pdu):
    return pickle.loads(binary_pdu)

def pdu_to_binary (pdu):
    return pickle.dumps(pdu)

def create_PDU(Type, data):
    return PDU(Type, data)

def select_file_name():
    pass

## remove a file from central server
def remove_file(file):

    data_to_send = file
    remove_pdu = create_PDU(Type='U', data=data_to_send)

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
    for file in peer_registered_entries:
        if remove_file(file):
            counter += 1
    if counter == len(peer_registered_entries):
        print("Successfully removed", counter, "entries from server")
        return True

## download file from another peer
def download_file(filename, ip, port):
    ## create TCP connection
    ## request download (D type PDU)
    ## recieve file (E,C or L type PDUs)
    pass





## create TCP socket listening to other peers requesting files in this peer
## port must be available (not in used by the others sockets)
## random port number? ask user? your choice!

## one socket for all other peers? one socket per peer? one socket per file? your choice!

## one socket for all peers approach:
## listen to other peers infinitely
## put this function in seperate thread? process? your choice!
def download_socket ():
    ## infinite service loop
    ## use select
    pass


## main driver
## ask user for input and answers user's requests according to input
# command = 'R'
while True:

    ## based on user input:
    ## O -> get files list from central server -> ask user for a file -> download that file
    ## L -> get local files
    ## R -> register a new file on central server
    ## U -> remove a registered file from central server
    ## E -> exit program
    print('*************\n\nInput Your command: ')
    command = input()

    if command == 'O':
        ## fetch files list from server
        ## ask user for specific file
        ## fetch that file's address from server
        ## download that file from the owner peer
        pass

    elif command == 'L':
        print("Files registered on the central server:")
        for file in peer_registered_entries:
            print(file)

    elif command == 'R':

        file = 'khiar.mkv'
        my_ip = str(socket.gethostbyname(socket.gethostname()))
        data_to_send = (my_ip, TCP_Port, file)
        register_pdu = create_PDU(Type='R', data=data_to_send)

        send_pdu_to_server(register_pdu)
        response_pdu = receive_server_pdu()

        response_pdu_type = response_pdu.t
        if response_pdu_type == 'A':
            peer_registered_entries.append(file)
            print('Server Response:', response_pdu.data.value)
        elif response_pdu_type == 'E':
            print('Server Response:', response_pdu.data.value)

    if command == 'U':

        file = 'khiar.mkv'
        if remove_file(file):
            peer_registered_entries.remove(file)

    if command == 'E':
        # print("\n\n********", peer_registered_entries, "*****")
        ## remove all registered files
        if exit_peer():
            exit()
