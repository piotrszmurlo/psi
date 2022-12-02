import sys
from socket import AF_INET, SOCK_DGRAM, socket

BUFSIZE = 512

if  len(sys.argv) < 2:
    raise Exception('No port')

port = int( sys.argv[1] )

print("UDP server up on port :", port)
with socket(AF_INET, SOCK_DGRAM) as s:
    s.bind(('', port))
    while True:
        data = s.recv(BUFSIZE).decode()

        print('Message received : ', data)
