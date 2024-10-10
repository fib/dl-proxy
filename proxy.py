import sys, socket
from urllib.parse import urlparse
from threading import Thread
import os
from enum import Enum

import logging
from typing import Callable


class Command(Enum):
    DOWNLOAD = 0x01


class Server:
    def __init__(self, host: int = socket.gethostname(), port: int = 1337) -> None:
        self.log = logging.getLogger("server")

        self.serversocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.serversocket.bind((host, port))

        self.log.info(f"server started at {self.serversocket.getsockname()}")

    def run(self, client_handler: Callable):
        self.serversocket.listen(5)

        while True:
            (clientsocket, address) = self.serversocket.accept()

            self.log.info(f"client connected: {address}")

            client = Thread(target=client_handler, args=[clientsocket, self.log])
            client.start()


def main():
    logging.basicConfig(level=logging.INFO)

    port = int(sys.argv[1])

    proxy = Server(port=port)

    def client_handler(sock: socket.socket, log: logging.Logger):
        while True:
            data = sock.recv(3)
            if data != b"":
                length = int.from_bytes(data[:2], byteorder="big")
                cmd = int.from_bytes(data[2:3], byteorder="little")
                args = sock.recv(length - 3).decode()

                log.info(
                    f"message received: {{sender: {sock.getpeername()}, length: {length}, cmd: {Command(cmd).name}, args: {args}}}"
                )

                target = {
                    'host': urlparse(args).netloc,
                    'port': 80,
                    'path': urlparse(args).path,
                    'filename': os.path.basename(urlparse(args).path)
                }

                target_request = f'GET {target["path"]} HTTP/1.1\r\nHost: {target["host"]}\r\nConnection: close\r\n\r\n'

                log.info(f'sending request to (\'{target["host"]}\', {target["port"]}): {repr(target_request)}')

                download_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                download_socket.connect((target['host'], target['port']))

                download_socket.send(target_request.encode())

                response = b''

                while True:
                    chunk = download_socket.recv(1024)
                    if len(chunk) == 0:
                        break
                    response += chunk                

                download_socket.close()


                header, body = response.split(b'\r\n\r\n')
                headers = {}

                for h in header.decode().split('\r\n'):
                    line = h.split(':')
                    if len(line) == 2:
                        headers[str.strip(line[0])] = str.strip(line[1])

                log.info(f'(\'{target["host"]}\', {target["port"]}) responded, content type = {headers["Content-Type"]}, content length = {headers["Content-Length"]}')

                with open (target['filename'], 'wb') as file:
                    file.write(body)

                log.info(f'wrote file to ./{target["filename"]}')
                
                # TODO: send file back
                sock.send(body)
                print('sent file')


    proxy.run(client_handler)


if __name__ == "__main__":
    main()
