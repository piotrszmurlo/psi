import random
import os
import socket
import struct
import time
import threading

RESOURCES_PATH = 'resources'
BUFFER_SIZE = 65535
PORT = 53290
TIMEOUT = 3  # seconds
MAX_NUMBER_OF_RETRIES = 3
DATAGRAM_LOSS_CHANCE = 0.5  # [0, 1]

BROADCAST_ADDRESS = "255.255.255.255"
HEADER_SIZE = 5  # sizeof(type: unsigned char + length: unsigned int)
STRUCT_FORMAT_HEADER = "!BI"


class DatagramType:
    BROADCAST_RESOURCES = 0
    FILE_DATA = 1
    REQUEST_FILE = 2


class Node:
    def __init__(self):
        os.makedirs(RESOURCES_PATH, exist_ok=True)
        self.available_resources = {}
        self.isStarted = False
        self.current_filename = ''

    def start(self):
        """Starts the node"""
        broadcast_thread = threading.Thread(target=self.broadcast_resources, daemon=True, name='Thread-broadcast')
        self.isStarted = True
        try:
            server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            server_socket.bind(('', PORT))
        except socket.error:
            print(f"{threading.current_thread().name}: Main socket creating error")
            exit(1)
        broadcast_thread.start()
        while self.isStarted:
            datagram, sender = server_socket.recvfrom(BUFFER_SIZE)
            sender_address = sender[0]
            datagram_type = datagram[0]
            args = (datagram, sender_address)
            if datagram_type == DatagramType.FILE_DATA:
                worker_thread = threading.Thread(target=self.on_file_data_received, args=args)
                worker_thread.start()
            elif datagram_type == DatagramType.BROADCAST_RESOURCES:
                worker_thread = threading.Thread(target=self.on_broadcast_resources_received, args=args)
                worker_thread.start()
            elif datagram_type == DatagramType.REQUEST_FILE:
                worker_thread = threading.Thread(target=self.on_request_file_received, args=args)
                worker_thread.start()

    def on_file_data_received(self, datagram, sender_address):
        if self.current_filename == '':
            return
        _, expected_length, file_contents = self.unpack_datagram(datagram)
        if expected_length != len(file_contents) + HEADER_SIZE:
            print(f"{threading.current_thread().name}: Received file data {self.current_filename} from {sender_address}"
                  f" is corrupted. Please retry.")
            self.current_filename = ''
            return
        with open(f"{RESOURCES_PATH}/{self.current_filename}", 'wb') as new_file:
            new_file.write(file_contents)
        print(f"{threading.current_thread().name}: Received file {self.current_filename} from {sender_address}")
        self.current_filename = ''

    def on_request_file_received(self, datagram: bytes, sender_address: str):
        _, _, filename = self.unpack_datagram(datagram)
        print(f"{threading.current_thread().name}: Received request from {sender_address} for file {filename}")
        if random.random() < DATAGRAM_LOSS_CHANCE:  # datagram loss simulation
            print(f"{threading.current_thread().name}: Outgoing file data datagram is lost!")
            return
        file_datagram = self.get_file_datagram(filename)
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as write_sock:
                write_sock.sendto(file_datagram, (sender_address, PORT))
        except socket.error as e:
            print(f"Send file socket error: {e}")
            return
        print(f'{threading.current_thread().name}: Sent "{filename}" to {sender_address}')

    def on_broadcast_resources_received(self, datagram, owner):
        _, _, filenames = self.unpack_datagram(datagram)
        for filename in filenames:
            if filename not in self.available_resources:
                self.available_resources[filename] = [owner]
            elif self.available_resources[filename] and owner not in self.available_resources[filename]:
                self.available_resources[filename].append(owner)

    def broadcast_resources(self):
        """Starts broadcasting current resources"""
        try:
            broadcast_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            broadcast_socket.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        except socket.error:
            print(f"{threading.current_thread().name}: Broadcast socket creating error")
            exit(1)
        while self.isStarted:
            resources_datagram = self.get_resources_datagram()
            try:
                broadcast_socket.sendto(resources_datagram, (BROADCAST_ADDRESS, PORT))
                time.sleep(5)
            except socket.error:
                print(f"{threading.current_thread().name}: Broadcast sendto() error")
                exit(1)

    def request_file(self, filename: str, source_address):
        """Sends a file request to source_address"""
        worker_thread = threading.Thread(target=self._request_file, args=(filename, source_address))
        worker_thread.start()

    def _request_file(self, filename: str, source_address, number_of_retries=0):
        data = self.get_request_file_datagram(filename)
        self.current_filename = filename
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as client_socket:
                client_socket.sendto(data, (source_address, PORT))
        except socket.error:
            print(f"{threading.current_thread().name}: Request file socket creating error")
            exit(1)
        time.sleep(TIMEOUT)
        if filename not in os.listdir(RESOURCES_PATH):
            if number_of_retries == MAX_NUMBER_OF_RETRIES:
                print(f"{threading.current_thread().name}: Timeout - max retries, aborting file request")
                self.current_filename = ''
                return
            print(f"{threading.current_thread().name}: Timeout - waited for {TIMEOUT} seconds and got no"
                  f" response from {source_address}, retrying file request")
            self._request_file(filename, source_address, number_of_retries+1)

    def get_request_file_datagram(self, filename: str):
        """Returns a datagram used to request a remote file from a peer"""
        type_ = DatagramType.REQUEST_FILE
        value = filename
        length = len(value) + HEADER_SIZE
        datagram = struct.pack(STRUCT_FORMAT_HEADER, type_, length) + value.encode()
        return datagram

    def get_resources_datagram(self):
        """Returns a datagram containing local files"""
        resource_list = os.listdir(RESOURCES_PATH)
        if not resource_list:
            return
        type_ = DatagramType.BROADCAST_RESOURCES
        value = ''
        for resource in resource_list[:-1]:
            value += (resource + '/')
        value += resource_list[-1]
        length = len(value) + HEADER_SIZE
        datagram = struct.pack(STRUCT_FORMAT_HEADER, type_, length) + value.encode()
        return datagram

    def get_file_datagram(self, filename: str):
        """Returns a datagram containing file data"""
        type_ = DatagramType.FILE_DATA
        with open(f"{RESOURCES_PATH}/{filename}", 'rb') as file:
            value = file.read()
        length = len(value) + HEADER_SIZE
        datagram = struct.pack(STRUCT_FORMAT_HEADER, type_, length) + value
        return datagram

    def unpack_datagram(self, datagram: bytes):
        """Unpacks datagram structure to type, value length and value"""
        type_, length = struct.unpack(STRUCT_FORMAT_HEADER, datagram[:HEADER_SIZE])
        value = datagram[HEADER_SIZE:]
        if type_ == DatagramType.BROADCAST_RESOURCES:
            value = value.decode().split('/')
        elif type_ == DatagramType.REQUEST_FILE:
            value = value.decode()
        return type_, length, value

    def get_available_files(self):
        """Returns remote files available to download"""
        local_resource_list = os.listdir(RESOURCES_PATH)
        available_files = [file for file in self.available_resources if file not in local_resource_list]
        return available_files
