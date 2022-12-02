import socket, struct, sys


def main():
    port = 53290
    buffer_size = 1024
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
        s.bind(('', port))
        print(f"Server started on port {port}")
        while True:
            datagram, address = s.recvfrom(buffer_size)
            if not datagram:
                print("Error in datagram?")
                break
            data = struct.unpack('<qih10s', datagram)
            print(f"Message from Client: {data}")
            print("Client IP Address:{}".format(address))


if __name__ == '__main__':
    main()
