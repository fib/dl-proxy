import sys, socket
# from enum import Enum
import logging

from proxy import Command

"""Constructs a packet given a command and arguments:

|   Message size (n)   |   Command   |             Arguments           |
|       2 bytes        |    1 byte   |          (n - 3) bytes          |
"""
def build_command(cmd: Command, args: str) -> bytes:
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

packet = build_command(Command.DOWNLOAD, "https://9p.io/plan9/img/plan9bunnywhite.jpg")

s.send(packet)

response = b''

while True:
    chunk = s.recv(1024)
    response += chunk            
    if len(chunk) < 1024:
        break

with open('output.jpg', 'wb') as file:
    file.write(response)

s.close()
print('done')