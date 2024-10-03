import socket

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

s.connect(("127.0.1.1", 1337))

while True:
    data = s.recv(1028)
    if data != b'':
        print(data)
        s.close()
        break