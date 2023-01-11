import logging
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


class DatagramType:
    BROADCAST_RESOURCES = 0
    FILE_DATA = 1
    REQUEST_FILE = 2


class Node:
    def __init__(self):
        os.makedirs(RESOURCES_PATH, exist_ok=True)
        self.available_resources = []
        self.isStarted = False

    def start(self):
        broadcast_thread = threading.Thread(target=self.broadcast_resources, daemon=True)
        self.isStarted = True
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        server_socket.bind(('', PORT))
        broadcast_thread.start()
        while True:
            datagram, sender = server_socket.recvfrom(BUFFER_SIZE)
            print(sender)
            print(socket.getsockname())
            hostname = socket.getfqdn()
            if datagram[0] == DatagramType.FILE_DATA:
                print(self.unpack_datagram(datagram))
            elif datagram[0] == DatagramType.BROADCAST_RESOURCES:
                self.on_broadcast_resources_received(datagram)
            elif datagram[0] == DatagramType.REQUEST_FILE:
                self.unpack_resources_datagram(datagram)

    def on_broadcast_resources_received(self, datagram):
        _, _, files = self.unpack_resources_datagram(datagram)
        for file in files:
            if file not in self.available_resources:
                self.available_resources.append(file)
        print(self.available_resources)

    def broadcast_resources(self):
        broadcast_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        broadcast_socket.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        while self.isStarted:
            print("sent bradcast")
            resources_datagram = self.get_resources_datagram()
            broadcast_socket.sendto(resources_datagram, ("255.255.255.255", PORT))
            time.sleep(5)

    def request_file(self, filename: str):
        data = self.get_request_file_datagram(filename)
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as client_socket:
            client_socket.sendto(data, ("127.0.0.1", PORT))

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

    def unpack_resources_datagram(self, datagram: bytes) -> tuple[int, int, list[str]]:
        type_, length, value = self.unpack_datagram(datagram)

        return type_, length, value.decode().split('/')

    def get_file_datagram(self, filename: str) -> Optional[bytes]:
        type_ = DatagramType.FILE_DATA
        value = ''
        try:
            with open(f"{RESOURCES_PATH}/{filename}", "r") as file:
                value += file.read()
        except FileNotFoundError:
            print(f'File "{filename}" not found!')
            return
        length = len(value) + HEADER_SIZE
        datagram = struct.pack(STRUCT_FORMAT_HEADER, type_, length) + value.encode()
        return datagram

    def unpack_datagram(self, datagram: bytes):
        type_, length = struct.unpack(STRUCT_FORMAT_HEADER, datagram[:HEADER_SIZE])
        value = datagram[HEADER_SIZE:]
        return type_, length, value
