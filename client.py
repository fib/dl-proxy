import sys, socket, os
from urllib.parse import urlparse

from proxy import Command

"""Constructs a packet given a command and arguments:

|   Message size (n)   |   Command   |             Arguments           |
|       2 bytes        |    1 byte   |          (n - 3) bytes          |
"""
def build_packet(cmd: Command, args: str) -> bytes:
    length = 2 + 1 + len(args)

    length = length.to_bytes(2, byteorder='big')
    cmd = cmd.value.to_bytes(1, byteorder='little')
    args = args.encode()

    packet = length + cmd + args

    return packet

host = sys.argv[1]
port = int(sys.argv[2])

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

s.connect((host, port))

print("Available commands and usage:")
print("1. Download file from url: `download url`")

command = input("Enter command: ")

cmd, args = command.split(' ')
url = urlparse(args)

packet = build_packet(Command[cmd], args)

s.send(packet)

response = b''

while True:
    chunk = s.recv(1024)
    response += chunk            
    if len(chunk) < 1024:
        break

with open(os.path.basename(url.path), 'wb') as file:
    file.write(response)

s.close()
print('done')