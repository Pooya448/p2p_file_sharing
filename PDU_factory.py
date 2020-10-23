from PDU import PDU

def create_RPDU(ip, port, file):
    return PDU(T='R', data=(ip, port, file))

def create_EPDU(error):
    return PDU(T='E', data=error)
#
def create_APDU(message):
    return PDU(T='A', data=message)
#
def create_UPDU(file):
    return PDU(T='U', data=file)
#
def create_OPDU():
    return PDU(T='O', data='')
#
def create_SPDU(file):
    return PDU(T='S', data=file)
#
# def create_RPDU():
#     return
#
# def create_RPDU():
#     return
