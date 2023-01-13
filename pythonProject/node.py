import random
import os
import socket
import struct
import time
from typing import Optional
import threading

RESOURCES_PATH = 'resources'
HEADER_SIZE = 5  # sizeof(type: unsigned char + length: unsigned int)
BUFFER_SIZE = 1024
STRUCT_FORMAT_HEADER = "!BI"
PORT = 53290
BROADCAST_ADDRESS = "255.255.255.255"


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
        broadcast_thread = threading.Thread(target=self.broadcast_resources, daemon=True)
        self.isStarted = True
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        server_socket.bind(('', PORT))
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
                worker_thread = threading.Thread(target=self.on_broadcast_resources_received,
                                                 args=args)
                worker_thread.start()
            elif datagram_type == DatagramType.REQUEST_FILE:
                worker_thread = threading.Thread(target=self.on_request_file_received, args=args)
                worker_thread.start()

    def on_file_data_received(self, datagram, sender_address):
        if self.current_filename == '':
            return
        _, _, file_contents = self.unpack_datagram(datagram)
        with open(f"{RESOURCES_PATH}/{self.current_filename}", 'w') as new_file:
            new_file.write(file_contents)
        print(f"{threading.current_thread().name}: Received file {self.current_filename} from {sender_address}")
        self.current_filename = ''

    def on_request_file_received(self, datagram: bytes, sender_address: str):
        _, _, filename = self.unpack_datagram(datagram)
        print(f"{threading.current_thread().name}: Got request from {sender_address} for file {filename}")
        file_datagram = self.get_file_datagram(filename)
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as write_sock:
            write_sock.sendto(file_datagram, (sender_address, PORT))
        print(f'{threading.current_thread().name}: Sent "{filename}" to {sender_address}')

    def on_broadcast_resources_received(self, datagram, owner):
        _, _, filenames = self.unpack_datagram(datagram)
        for filename in filenames:
            if filename not in self.available_resources:
                self.available_resources[filename] = [owner]
            elif self.available_resources[filename] and owner not in self.available_resources[filename]:
                self.available_resources[filename].append(owner)

    def broadcast_resources(self):
        broadcast_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        broadcast_socket.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        while self.isStarted:
            resources_datagram = self.get_resources_datagram()
            broadcast_socket.sendto(resources_datagram, (BROADCAST_ADDRESS, PORT))
            time.sleep(5)

    def request_file(self, filename: str):
        data = self.get_request_file_datagram(filename)
        source_address = random.choice(self.available_resources[filename])
        self.current_filename = filename
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as client_socket:
            client_socket.sendto(data, (source_address, PORT))

    def get_request_file_datagram(self, filename: str):
        type_ = DatagramType.REQUEST_FILE
        value = filename
        length = len(value) + HEADER_SIZE
        datagram = struct.pack(STRUCT_FORMAT_HEADER, type_, length) + value.encode()
        return datagram

    def get_resources_datagram(self) -> Optional[bytes]:
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

    def get_file_datagram(self, filename: str) -> Optional[bytes]:
        type_ = DatagramType.FILE_DATA
        value = ''
        with open(f"{RESOURCES_PATH}/{filename}", 'r') as file:
            value += file.read()
        length = len(value) + HEADER_SIZE
        datagram = struct.pack(STRUCT_FORMAT_HEADER, type_, length) + value.encode()
        return datagram

    def unpack_datagram(self, datagram: bytes):
        type_, length = struct.unpack(STRUCT_FORMAT_HEADER, datagram[:HEADER_SIZE])
        value = datagram[HEADER_SIZE:].decode()
        if type_ == DatagramType.BROADCAST_RESOURCES:
            value = value.split('/')
        return type_, length, value

    def get_available_files(self):
        """Returns remote files available to download"""
        local_resource_list = os.listdir(RESOURCES_PATH)
        available_files = [file for file in self.available_resources if file not in local_resource_list]
        return available_files
