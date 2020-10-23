from enum import Enum


class Error(Enum):
    RegisterFail = 'File already exists.'
    FileNotFound = 'The requested file does not exist'
    deleteFail = 'There was an error deleting requested file'
    ServerEmpty = 'Server does not contain any files by the time of request.'

class Success(Enum):
    RegisterOK = 'File successfully registered.'
    DeleteOK = 'File successfully removed.'
    ListRetrieveOK = 'OK'
