import pickle

buffer_size = 1024
download_buffer_size = 187

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
    return pickle.dumps(pdu)
