import socket
import time


def work():
    return True


def more_data():
    return True


def main():
    port = 53290
    buffer_size = 8
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(('', port))
        print(f"Server listening on port {port}")
        s.listen()
        while work():
            try:
                connection, address = s.accept()
            except socket.timeout:
                print("accept() timeout, restarting...")
                continue
            except KeyboardInterrupt:
                print("accept() interrupted, ending.")
                exit(-1)
            with connection:
                print(f"Connection from address: {address}")
                while more_data():
                    data = connection.recv(buffer_size)
                    if not data:
                        break
                    print(f"Message from Client: {data}")
            connection.close()


if __name__ == '__main__':
    main()
