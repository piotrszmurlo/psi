import threading

from node import Node


class CommandType:
    QUIT = 'q'
    GET = 'get'
    LIST = 'ls'


def main():
    node = Node()
    background_thread = threading.Thread(target=node.start, daemon=True)
    background_thread.start()

    print("q -> quit")
    print("ls -> list available files")
    print('get "[filename]" -> download a file')
    command = input("Input command: ")
    while command != CommandType.QUIT:
        if command == CommandType.LIST:
            available_files = node.get_available_files()
            if not available_files:
                print("No remote files available")
            else:
                print(available_files)
        if command.startswith(CommandType.GET):
            command.split('"')
        command = input("Input command: ")


if __name__ == '__main__':
    main()
