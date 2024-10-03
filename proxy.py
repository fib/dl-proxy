import sys, socket
from threading import Thread
import logging

port = int(sys.argv[1])

logger = logging.getLogger('proxy')
logging.basicConfig(level=logging.INFO)

# setup and start server socket
serversocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
serversocket.bind((socket.gethostname(), port))
serversocket.listen(5)

logger.info(f'server started: {serversocket}')

def handle_socket(sock):
    sock.send(b'hi')

while True:
    (clientsocket, address) = serversocket.accept()

    logger.info(f'client connected: {address}')

    client = Thread(target=handle_socket, args=[clientsocket])
    client.run()