import socket


def main():
    port = 53290
    buffer_size = 1024
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(('', port))
        print(f"Server listening on port {port}")
        while True:
            s.listen()
            connection, address = s.accept()
            with connection:
                print(f"Connection from address: {address}")
                data = connection.recv(buffer_size)
                if not data:
                    print("Data error")
                    break
                print(f"Message from Client: {data}")


if __name__ == '__main__':
    main()
