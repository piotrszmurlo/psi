import socket


def work():
    return True


def more_data():
    return True


def main():
    port = 53290
    buffer_size = 8
    backlog = 5
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(('', port))
        print(f"Server listening on port {port}")
        s.listen(backlog)
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
                data = ''
                initial = True
                split_message = []
                while more_data():
                    temp_data = connection.recv(buffer_size)
                    if not temp_data:
                        break
                    # only the first data portion contains message length
                    if initial:
                        split_message = temp_data.decode().split('\0')
                        if len(split_message) == 2:
                            data += split_message[1]
                        initial = False
                    else:
                        data += temp_data.decode()
                    if len(data) >= int(split_message[0]):
                        connection.sendall(b'received, thanks')
                        break
                print(f"Message from Client: {data}")

            connection.close()


if __name__ == '__main__':
    main()
