import os
import threading

from node import Node, RESOURCES_PATH


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
    command = input()
    initial = True
    while command != CommandType.QUIT:
        if not initial:
            command = input()
        initial = False 
        if command == CommandType.LIST:
            available_files = node.get_available_files()
            if not available_files:
                print("No remote files available")
            else:
                print(available_files)
        if command.startswith(CommandType.GET):
            filename = command.removeprefix('get "').removesuffix('"')
            if filename in os.listdir(RESOURCES_PATH):
                print("File is available locally.")
                continue
            elif filename not in node.get_available_files():
                print("Filename does not match any available file.")
                continue
            else:
                sources = node.available_resources[filename]
                if len(sources) == 1:
                    node.request_file(filename, sources[0])
                    continue
                print("Choose source address:")
                indexes = []
                for index, address in enumerate(sources):
                    print(f"{index}: {address}")
                    indexes.append(index)
                source_index = input()
                if int(source_index) not in indexes:
                    print("Incorrect source index, aborting")
                    continue
                node.request_file(filename, sources[int(source_index)])


if __name__ == '__main__':
    main()
