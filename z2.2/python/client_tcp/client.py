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
        try:
            s.connect((host, port))
        except ConnectionError:
            print("connection error, quitting")
            exit(-1)
        message = b"abcdefghijklmnoprs"
        message_with_len = str(len(message)).encode() + b'\0' + message
        s.sendall(message_with_len)
        print("data sent")
        data = s.recv(buffer_size)
        if not data:
            print("data error")
        print(f"Message from server: {data}")


if __name__ == '__main__':
    main()
