import socket, sys
from socket import gethostbyname


def main():
    port = 53290
    buffer_size = 1024
    if len(sys.argv) != 2:
        print("Provide hostname as command line argument")
        exit(-1)
    try:
        host = gethostbyname(sys.argv[1])
    except socket.gaierror:
        print("Error: Host name can't be resolved")
        exit(-1)
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((host, port))
        s.sendall(b"abcdefghijk")
        print("data sent")
        data = s.recv(buffer_size)
        if not data:
            print("data error")
        print(f"Message from server: {data}")


if __name__ == '__main__':
    main()
