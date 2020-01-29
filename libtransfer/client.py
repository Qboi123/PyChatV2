# client.py

import math

import socket                   # Import socket module

print("Your Hostname is: %s " % socket.gethostname())
host = input("IP: ")

server = socket.socket()             # Create a socket object
# host = socket.gethostname()     # Get local machine name
print(host)
port = 60000                    # Reserve a port_ for your service.

server.connect((host, port))

current_dir = "/"

import os

while 1:
    a = input("> ")

    text = a
    cmd_and_params = text.split(" ")
    cmd = cmd_and_params[0]
    params = cmd_and_params[1:]

    if cmd in ["get", "cd", "listdir", "exit", "curdir", "dir"]:
        server.send(a.encode())
    else:
        continue

    data = server.recv(int(4500000000))

    fileCmd = a.split(" ", maxsplit=1)
    Cmd = a.split(" ")

    if fileCmd[0] == "get":
        with open(" ".join(params), "wb+") as file:
            file.write(data)

    elif cmd in ["cd", "listdir", "curdir", "dir"]:
        print(data.decode())
    elif cmd == "listdir":
        print(data.decode())
    elif cmd == "exit":
        print("Exited!")
    else:
        pass
    #
    # filename = server.recv(0)
    # with open(filename, 'wb+') as f:
    #     print('file opened')
    #     while True:
    #         print('receiving data...')
    #         data = server.recv(-1)
    #         print('data=%s', (data))
    #         if not data:
    #             break
    #         # write data to a file
    #         f.write(data)

f.close()
print('Successfully get the file')
server.close()
print('connection closed')