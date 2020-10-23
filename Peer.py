
import socket
import select
import pickle
from message import Error, Success
from PDU_factory import create_RPDU, create_UPDU, create_OPDU, create_SPDU, create_FPDU, create_LPDU, create_DPDU
import sys
import threading
import random

peer_registered_entries = []
## create UDP socket in order to connect to central server
# client_greet_message = "Fuck you server!"
# client_greet_message_bytes = str.encode(client_greet_message)

server_address_port= ("127.0.0.1", 8888)
buffer_size = 1024
download_buffer_size = 187

TCP_PORT = random.randint(5000, 9000)
# TCP_download_Port = 6666
HOST_IP = "127.0.0.1"

# TCP_upload_socket = socket.socket(family=socket.AF_INET, type=socket.SOCK_STREAM)
# TCP_upload_socket.bind(('127.0.0.1', TCP_Port))
# serversocket.bind((socket.gethostname(), 80))


UDP_peer_socket = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)




def send_pdu_to_server(bytes_to_send):
    bytes_to_send = pdu_to_binary(bytes_to_send)
    UDP_peer_socket.sendto(bytes_to_send, server_address_port)

def receive_server_pdu():
    server_response = UDP_peer_socket.recvfrom(buffer_size)[0]
    response_pdu = binary_to_pdu(server_response)
    return response_pdu

def receive_pdu(socket):
    recieved_bytes = socket.recv(buffer_size)
    recieved_pdu = binary_to_pdu(recieved_bytes)
    return recieved_pdu

def send_pdu(pdu, socket):
    bytes_to_send = pdu_to_binary(pdu)
    socket.sendall(bytes_to_send)

def binary_to_pdu (binary_pdu):
    return pickle.loads(binary_pdu)

def pdu_to_binary (pdu):
    # print(sys.getsizeof(pdu))
    return pickle.dumps(pdu)

# def create_PDU(Type, data):
#     return PDU(Type, data)

def select_file_name():
    pass

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
    # print(recieved_bytes)
    print("DL data: ", sys.getsizeof(recieved_bytes))
    recieved_pdu = binary_to_pdu(recieved_bytes)
    return recieved_pdu

def download_file(filename, ip, port):

    socket = initialize_download_socket()
    request_download(filename, socket, ip, port)

    # request_pdu = create_DPDU(filename)
    # bytes_to_send = pdu_to_binary(request_pdu)
    #
    # TCP_download_socket = socket.socket(family=socket.AF_INET, type=socket.SOCK_STREAM)
    # TCP_download_socket.connect((ip, port))
    # TCP_download_socket.sendall(bytes_to_send)

    chunks = []

    last_pdu = download_next_chunk(socket)
    # recieved_bytes = socket.recv(download_buffer_size)
    # print(recieved_bytes)
    # print("DL data: ", sys.getsizeof(recieved_bytes))
    # last_pdu = binary_to_pdu(recieved_bytes)

    last_pdu_type = last_pdu.t
    chunks.append(last_pdu.data.decode())

    while last_pdu_type != 'L':
        # recieved_bytes = socket.recv(download_buffer_size)
        # recieved_pdu = binary_to_pdu(recieved_bytes)
        last_pdu = download_next_chunk(socket)
        # last_pdu = recieved_pdu
        last_pdu_type = last_pdu.t
        chunks.append(last_pdu.data.decode())

    data = ''.join(chunks)
    print(data)

    # TCP_download_socket.shutdown(socket.SHUT_RDWR)
    socket.close()
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

def upload_file(socket, file):
    with open(file, 'rb') as file:
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
                bytes_to_send = pdu_to_binary(response_pdu)
                print("UL data: ", sys.getsizeof(bytes_to_send))
                # socket.sendall(bytes_to_send)

                counter = 0
                bytes100 = bytes()
    response_pdu = create_LPDU(bytes100)
    send_pdu(response_pdu, socket)
    bytes_to_send = pdu_to_binary(response_pdu)
    print("UL data: ", sys.getsizeof(bytes_to_send))
    # socket.sendall(bytes_to_send)
    return True

### creating a deamon for TCP socket
TCP_Daemon = threading.Thread(target=upload_request_handler, args=(TCP_PORT, HOST_IP), daemon=True)
TCP_Daemon.start()


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
    # command = 'O'
    if command == 'O':

        ## fetch files list from server
        if retrieve_files():
            ## ask user for specific file
            print("Enter the name of file to download:")
            # selected_file = input()
            selected_file = 'khiar.txt'
            if selected_file in peer_registered_entries:
                print("File already exist in local")
                # pass
            ## fetch that file's address from server
            host_ip, host_port = retrieve_file_address(selected_file)
            ## download that file from the owner peer
            download_file(selected_file, host_ip, host_port)
            command = ''

    elif command == 'L':
        if any(peer_registered_entries):
            print("Files registered on the central server:")
            for file in peer_registered_entries:
                print(file)
        else:
            print("There are no local files by now.")

    elif command == 'R':
        # print("Enter file name to register:")
        # file = input()
        file = 'khiar.txt'
        register_file(file)

    if command == 'U':
        # print("Enter file name to delete from server:")
        # file = input()
        file = 'khiar.txt'
        if remove_file(file):
            peer_registered_entries.remove(file)

    if command == 'E':
        # print("\n\n********", peer_registered_entries, "*****")
        ## remove all registered files
        if exit_peer():
            exit()
