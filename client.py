import sys, socket, os
from urllib.parse import urlparse

from proxy import Command


def build_packet(cmd: Command, args: str) -> bytes:
    """Constructs a packet given a command and arguments:

    |   Message size (n)   |   Command   |             Arguments           |
    |       2 bytes        |    1 byte   |          (n - 3) bytes          |
    """
    length = 2 + 1 + len(args)

    length = length.to_bytes(2, byteorder="big")
    cmd = cmd.value.to_bytes(1, byteorder="little")
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

cmd, args = command.split(" ")
url = urlparse(args)
filename = os.path.basename(url.path)

packet = build_packet(Command[cmd], args)

s.send(packet)

response = b""

while True:
    chunk = s.recv(1024)
    response += chunk
    if len(chunk) < 1024:
        break

with open(filename, "wb") as file:
    file.write(response)

s.close()
print(f"data written to ./{filename}")
