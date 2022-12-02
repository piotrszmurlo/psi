import sys
from socket import AF_INET, SOCK_DGRAM, socket, gethostbyname

if  len(sys.argv) < 3:
    raise Exception('Agruments: hostname, port')

port = int( sys.argv[2] )
host = gethostbyname(sys.argv[1])

print("Will send to ", host, ":", port)

datagrams = ["1 koza\n", "2 kozy\n", "3 kozy\n", "4 kozy\n", "5 koz\n"]

with socket(AF_INET, SOCK_DGRAM) as s:
    for datagram in datagrams:

        print('Sending ...')
        s.sendto(datagram.encode(), (host, port))


print('Client finished.')
