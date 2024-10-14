import sys, socket
from urllib.parse import urlparse
from threading import Thread
import os
from enum import Enum

import logging
from typing import Callable


class Command(Enum):
    download = 0x01


class Server:

    def __init__(self, host: str = socket.gethostname(), port: int = 1337) -> None:
        """Initializes a Server object."""

        self.log = logging.getLogger("server")

        self.serversocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.serversocket.bind((host, port))

        self.log.info(f"server started at {self.serversocket.getsockname()}")

    def run(self, client_handler: Callable = None) -> None:
        """Starts the server socket and assigns a client handler.
        Default handler is `Server.download`.
        """

        if client_handler == None:
            client_handler = Server.__client_handler

        self.serversocket.listen(5)

        while True:
            (clientsocket, address) = self.serversocket.accept()

            self.log.info(f"client connected: {address}")

            client = Thread(target=client_handler, args=[self, clientsocket])
            client.start()

    def __client_handler(self, client: socket.socket) -> None:
        """The default client handler.
        Expects an initial message of size 3 containing the message size and command:
        |   Message size (n)   |   Command   |
        |       2 bytes        |    1 byte   |

        Then, another message of size (n-3) containing the arguments for the command.
        Commands are defined in the `Command` enum class.
        """

        data = client.recv(3)
        if data != b"":
            length = int.from_bytes(data[:2], byteorder="big")
            cmd = int.from_bytes(data[2:3], byteorder="little")
            args = client.recv(length - 3).decode()

            self.log.info(
                f"message received from {client.getpeername()}: {{length: {length}, cmd: {Command(cmd).name}, args: {args}}}"
            )

            match cmd:
                case Command.download.value:
                    self.__download(client, args)

    def __download(self, client: socket.socket, args: str) -> None:
        """Download command handler: establishes a socket to a remote server and downloads a file,
        saving a copy on the proxy server and sending the file back to the client.
        Expects a URL pointing directly to a file as argument.
        """

        url = urlparse(args)
        target = {
            "host": url.netloc,
            "port": 80,
            "path": url.path,
            "filename": os.path.basename(url.path),
        }

        # connect to remote server and download file

        download_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        download_socket.connect((target["host"], target["port"]))

        target_request = f'GET {target["path"]} HTTP/1.1\r\nHost: {target["host"]}\r\nConnection: close\r\n\r\n'

        self.log.info(
            f'sending request to (\'{target["host"]}\', {target["port"]}): {repr(target_request)}'
        )

        download_socket.send(target_request.encode())

        response = b""

        while True:
            chunk = download_socket.recv(1024)
            if len(chunk) == 0:
                break
            response += chunk

        download_socket.close()

        # parse remote server response

        header, body = response.split(b"\r\n\r\n")
        headers = {}

        for h in header.decode().split("\r\n"):
            line = h.split(":")
            if len(line) == 2:
                headers[str.strip(line[0])] = str.strip(line[1])

        self.log.info(
            f'(\'{target["host"]}\', {target["port"]}) responded, content type = {headers["Content-Type"]}, content length = {headers["Content-Length"]}'
        )

        # save a copy of the returned file on the proxy server

        with open(f'proxy_{target["filename"]}', "wb") as file:
            file.write(body)

        self.log.info(f'wrote file to ./proxy_{target["filename"]}')

        # send the file back to the client

        self.log.info(f'sending "{target["filename"]}" to {client.getpeername()}')
        client.send(body)

        self.log.info(f"transmission to {client.getpeername()} done, closing socket")
        client.close()


def main():
    logging.basicConfig(level=logging.INFO)

    port = int(sys.argv[1])
    proxy = Server(port=port)

    proxy.run()


if __name__ == "__main__":
    main()
