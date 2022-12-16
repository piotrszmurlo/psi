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
        print(f"host address: {host}")
    except socket.gaierror:
        print("Error: Host name can't be resolved")
        exit(-1)
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((host, port))
        message = b"abcdefghijk"
        s.sendall(message)
        print(f"data sent: '{message.decode()}'")
        data = s.recv(buffer_size)
        if not data:
            print("data error")
        print(f"Message from server: {data}")
    s.close()


if __name__ == '__main__':
    main()
