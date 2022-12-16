import socket, sys
from socket import gethostbyname


def main():
    port = 53290
    try:
        host = gethostbyname(sys.argv[1])
    except socket.gaierror:
        print("Error: Host name can't be resolved")
        exit(-1)


    if len(sys.argv) != 2:
        print("Provide port as command line argument")
        exit(-1)

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((host, port))
        # try:
        print(s.send(b"abcdefghijkabcdefghijk"*3000))
        # except Exception:
        #     print("Error: send failed")
        #     exit(-1)


if __name__ == '__main__':
    main()
