import socket, sys
from socket import gethostbyname


def main():
    port = 53290
    host = gethostbyname(sys.argv[1])

    if len(sys.argv) < 2:
        raise Exception('Arguments: hostname')

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((host, port))
        s.sendall(b"abcdefghi")

if __name__ == '__main__':
    main()
