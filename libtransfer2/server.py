# server.py

import socket                   # Import socket module
import os
import threading

port = 60000                    # Reserve a port_ for your service.
s = socket.socket()             # Create a socket object
host = socket.gethostname()     # Get local machine name
s.bind((host, port))            # Bind to the port_
s.listen(5)                     # Now wait for client connection.

print('Server listening....')

os.chdir("/")


def runner(conn, addr):
    curdir = "/"
    while 1:
        data = conn.recv(1024)
        print('Server received', repr(data))

        text = data.decode()
        cmd_and_params = text.split(" ")
        cmd = cmd_and_params[0]
        params = cmd_and_params[1:]

        if cmd == "get":
            filepath = os.path.join(os.getcwd(), " ".join(params))
            with open(filepath, "rb") as file:
                data = file.read()
                conn.send(data)
        elif cmd == "cd":
            filepath = curdir+"/"+"".join(params)
            curdir = filepath
            os.chdir("".join(params))
            conn.send(b"Successfully Changed Directory")
        elif cmd == "listdir" or cmd == "dir" or cmd == "ld":
            filepath = curdir+"/"+"".join(params)
            list = os.listdir(".")

            Str = "Files:\n"
            for i in list:
                Str += "  {file} | size={size}\n".format(file=i, size=os.path.getsize(os.path.join(os.getcwd(), " ".join(params), i)))
            conn.send(Str.encode())
        elif cmd == "/exit":
            conn.close()
        elif cmd == "curdir":
            conn.send(os.getcwd().encode())

while True:
    conn, addr = s.accept()     # Establish connection with client.
    print('Got connection from', addr)
    threading.Thread(None, runner, args=(conn, addr)).start()
    # filename='mytext.txt'
    #
    # conn.send(b"%s" % filename)
    # f = open(filename,'rb')
    # l = f.read(1024)
    # while (l):
    #    conn.send(l)
    #    print('Sent ', repr(l))
    #    l = f.read(1024)
    # f.close()
    #
    # print('Done sending')
    # # conn.send(b'File: ' % )
    # conn.close()

