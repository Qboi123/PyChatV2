
# Importeren sys module
import sys
import threading
import socket
import math
from random import randint as RandomInt

# Versie checken.
if not sys.hexversion > 0x03000000:
    version = 2
else:
    version = 3
if len(sys.argv) > 1 and sys.argv[1] == "-cli":
    print("Start commandolijn chat op...")
    isCLI = True
else:
    isCLI = False

# Tkinter module importeren via versie.
if version == 3:
    from tkinter import *
    from tkinter.ttk import *
    from tkinter import colorchooser
    from tkinter.filedialog import asksaveasfilename
else:
    print("This program is only supported for Python 3.x")
    input()

# == Importeren modules resterende. ========================

# Globals variabelen instellen
conn_array = []  # stores open sockets
secret_array = dict()  # key: the open sockets in conn_array,
# value: integers for encryption
username_array = dict()  # key: the open sockets in conn_array,
# value: usernames for the connection
contact_array = dict()  # key: ip address as a string, value: [port, username]
max_len = 102

# Stelt de gebruikersnaam in
username = "Ik"
usercolor = "#007f7f"
colorlist = ()
# usercolor = input('Kleur: ').lower()

# Stelt de Server setup in
location = 0
port = 0
top = ""

# STARTUP SETTINGS
welcomeSign = False
titleText = "Py Chat"
chatVersion = "v2.1"

main_body_text = 0


# So,
#  x_encode your message with the key, then pass that to
#  refract to get a string out of it.
# To decrypt, pass the message back to x_encode, and then back to refract

def binWord(word):
    """Converts the string into binary."""
    master = ""
    for letter in word:
        temp = bin(ord(letter))[2:]
        while len(temp) < 7:
            temp = '0' + temp
        master = master + temp
    return master


def xcrypt(message, key):
    """Encrypts the binary message by the binary key."""
    count = 0
    master = ""
    for letter in message:
        if count == len(key):
            count = 0
        master += str(int(letter) ^ int(key[count]))
        count += 1
    return master


def x_encode(string, number):
    """Encrypts the string by the number."""
    return xcrypt(binWord(string), bin(number)[2:])


def refract(binary):
    """Returns the string representation of the binary.
    Has trouble with spaces.

    """
    master = ""
    for x in range(0, int(len(binary) / 7)):
        master += chr(int(binary[x * 7: (x + 1) * 7], 2) + 0)
    return master


def formatNumber(number):
    """Ensures that number is at least length 4 by
    adding extra 0s to the front.

    """
    temp = str(number)
    while len(temp) < 4:
        temp = '0' + temp
    return temp


def netSend(conn, secret, message):
    """Sends message through the open socket conn with the encryption key
    secret. Sends the length of the incoming message, then sends the actual
    message.

    """
    try:
        conn.send(formatNumber(len(x_encode(message, secret))).encode())
        conn.send(x_encode(message, secret).encode())
    except socket.error:
        if len(conn_array) != 0:
            writeError(
                "Verbindings melding. Verzenden bericht mislukt", "server")
            processFlag("-001")


def netCatch(conn, secret):
    """Receive and return the message through open socket conn, decrypting
    using key secret. If the message length begins with - instead of a number,
    process as a flag and return 1.

    """
    try:
        data = conn.recv(4)
        if data.decode()[0] == '-':
            processFlag(data.decode(), conn)
            return 1
        data = conn.recv(int(data.decode()))
        return refract(xcrypt(data.decode(), bin(secret)[2:]))
    except socket.error:
        if len(conn_array) != 0:
            writeError(
                "Verbindings melding. Aankomen van een bericht mislukt", "server")
        processFlag("-001")


def isPrime(number):
    """Checks to see if a number is prime."""
    x = 1
    if number == 2 or number == 3:
        return True
    while x < math.sqrt(number):
        x += 1
        if number % x == 0:
            return False
    return True


def processFlag(number, conn=None):
    """Process the flag corresponding to number, using open socket conn
    if necessary.

    """
    global statusConnect
    global conn_array
    global secret_array
    global username_array
    global contact_array
    global isCLI
    t = int(number[1:])
    if t == 1:  # disconnect
        # in the event of single connection being left or if we're just a
        # client
        if len(conn_array) == 1:
            writeError("Verbinding verbroken", "server")
            dump = secret_array.pop(conn_array[0])
            dump = conn_array.pop()
            try:
                dump.close()
            except socket.error:
                print("Verbinding verbroken door slechte connectie.")
            if not isCLI:
                statusConnect.set("Lanceer")
                connecter.config(state=NORMAL)
            return

        if conn != None:
            writeError("Verbinding " + conn.getsockname()
            [0] + " verbroken", "server")
            dump = secret_array.pop(conn)
            conn_array.remove(conn)
            conn.close()

    if t == 2:  # username change
        name = netCatch(conn, secret_array[conn])
        if (isUsernameFree(name)):
            writeToScreen('white', "blue",
                          "Gebruiker " + username_array[conn] + " heeft zijn naam gewijzigd naar: " + name, "server")
            username_array[conn] = name
            contact_array[
                conn.getpeername()[0]] = [conn.getpeername()[1], name]

    # passing a friend who this should connect to (I am assuming it will be
    # running on the same port as the other session)
    if t == 4:
        data = conn.recv(4)
        data = conn.recv(int(data.decode()))
        Client(data.decode(),
               int(contact_array[conn.getpeername()[0]][0])).start()


def processUserCommands(command, param):
    """Processes commands passed in via the / text input."""
    global conn_array
    global secret_array
    global username

    if command == "nick":  # change nickname
        for letter in param[0]:
            if letter == " " or letter == "\n":
                if isCLI:
                    error_window(0, "Ongeldige naam. Geen spaties!")
                else:
                    error_window(root, "Ongeldige naam. Geen spaties!")
                return
        if isUsernameFree(param[0]):
            writeSucces("Naam gewijzigd naar: '" + param[0] + "'", "server")
            for conn in conn_array:
                conn.send("-002".encode())
                netSend(conn, secret_array[conn], param[0])
            username = param[0]
        else:
            writeError(param[0] +
                       " wordt al gebruikt als naam!", "client")
    if command == "disconnect":  # disconnects from current connection
        for conn in conn_array:
            conn.send("-001".encode())
        processFlag("-001")
    if command == "connect":  # connects to passed in host port
        if (options_sanitation(param[1], param[0])):
            Client(param[0], int(param[1])).start()
    if command == "host":  # starts server on passed in port
        if (options_sanitation(param[0])):
            Server(int(param[0])).start()


def isUsernameFree(name):
    """Checks to see if the username name is free for use."""
    global username_array
    global username
    for conn in username_array:
        if name == username_array[conn] or name == username:
            return False
    return True


def passFriends(conn):
    """Sends conn all of the people currently in conn_array so they can connect
    to them.

    """
    global conn_array
    for connection in conn_array:
        if conn != connection:
            conn.send("-004".encode())
            conn.send(
                formatNumber(len(connection.getpeername()[0])).encode())  # pass the ip address
            conn.send(connection.getpeername()[0].encode())
            # conn.send(formatNumber(len(connection.getpeername()[1])).encode()) #pass the port number
            # conn.send(connection.getpeername()[1].encode())


# --------------------------------------------------------------------------

def client_options_window(master):
    """Launches client options window for getting destination hostname
    and port.

    """
    top = Toplevel(master)
    top.title("Connection options")
    top.protocol("WM_DELETE_WINDOW", lambda: optionDelete(top))
    top.grab_set()
    Label(top, text="Server IP-adres:").grid(row=0)
    location = Entry(top)
    location.grid(row=0, column=1)
    location.focus_set()
    Label(top, text="Poort:").grid(row=1)
    port = Entry(top)
    port.grid(row=1, column=1)
    go = Button(top, text="Verbind", command=lambda:
    client_options_go(location.get(), port.get(), top))
    go.grid(row=2, column=1)


def client_options_go(dest, port, window):
    "Processes the options entered by the user in the client options window."""
    if options_sanitation(port, dest):
        if not isCLI:
            window.destroy()
        Client(dest, int(port)).start()
    elif isCLI:
        sys.exit(1)


def options_sanitation(por, loc=""):
    """Checks to make sure the port and destination ip are both valid.
    Launches error windows if there are any issues.

    """
    global root
    if isCLI:
        root = 0
    if not por.isdigit():
        error_window(root, "Voer een poort nummer in a.u.b.")
        return False
    if int(por) < 0 or 65555 < int(por):
        error_window(root, "Voer a.u.b. een poort code tussen 0 en 65555")
        return False
    if loc != "":
        if not ip_process(loc.split(".")):
            error_window(root, "Voer a.u.b. een gelding IP-adres in")
            return False
    return True


def ip_process(ipArray):
    """Checks to make sure every section of the ip is a valid number."""
    if len(ipArray) != 4:
        return False
    for ip in ipArray:
        if not ip.isdigit():
            return False
        t = int(ip)
        if t < 0 or 255 < t:
            return False
    return True


# ------------------------------------------------------------------------------

def server_options_window(master):
    """Launches server options window for getting port."""
    top = Toplevel(master)
    top.title("Verbindings opties")
    top.grab_set()
    top.protocol("WM_DELETE_WINDOW", lambda: optionDelete(top))
    Label(top, text="Poort:").grid(row=0)
    port = Entry(top)
    port.grid(row=0, column=1)
    port.focus_set()
    go = Button(top, text="Lanceer", command=lambda:
    server_options_go(port.get(), top))
    go.grid(row=1, column=1)


def server_options_go(port, window):
    """Processes the options entered by the user in the
    server options window.

    """
    if options_sanitation(port):
        if not isCLI:
            window.destroy()
        Server(int(port)).start()
    elif isCLI:
        sys.exit(1)


# -------------------------------------------------------------------------

def username_options_window(master):
    """Launches username options window for setting username."""
    top = Toplevel(master)
    top.title("Gebruikers opties")
    top.grab_set()
    Label(top, text="Naam:").grid(row=0)
    name = Entry(top)
    name.focus_set()
    name.grid(row=0, column=1)
    go = Button(top, text="Wijzig", command=lambda:
    username_options_go(name.get(), top))
    go.grid(row=1, column=1)


def username_options_go(name, window):
    """Processes the options entered by the user in the
    server options window.

    """
    processUserCommands("nick", [name])
    window.destroy()


# -------------------------------------------------------------------------

def error_window(master, texty=""):
    """Launches a new window to display the message texty."""
    global isCLI
    if isCLI:
        writeError(texty, "errMain")
    else:
        window = Toplevel(master)
        window.title("ERROR")
        window.grab_set()
        Label(window, text=texty).pack()
        go = Button(window, text="OKÉ", command=window.destroy)
        go.pack()
        go.focus_set()


def optionDelete(window):
    connecter.config(state=NORMAL)
    window.destroy()


# -----------------------------------------------------------------------------
# Contacts window

def contacts_window(master):
    """Displays the contacts window, allowing the user to select a recent
    connection to reuse.

    """
    global contact_array
    cWindow = Toplevel(master)
    cWindow.title("Contacten")
    cWindow.grab_set()
    scrollbar = Scrollbar(cWindow, orient=VERTICAL)
    listbox = Listbox(cWindow, yscrollcommand=scrollbar.set)
    scrollbar.config(command=listbox.yview)
    scrollbar.pack(side=RIGHT, fill=Y)
    buttons = Frame(cWindow)
    cBut = Button(buttons, text="Verbind",
                  command=lambda: contacts_connect(
                      listbox.get(ACTIVE).split(" ")))
    cBut.pack(side=LEFT)
    dBut = Button(buttons, text="Verwijder",
                  command=lambda: contacts_remove(
                      listbox.get(ACTIVE).split(" "), listbox))
    dBut.pack(side=LEFT)
    aBut = Button(buttons, text="Voeg toe",
                  command=lambda: contacts_add(listbox, cWindow))
    aBut.pack(side=LEFT)
    buttons.pack(side=BOTTOM)

    for person in contact_array:
        listbox.insert(END, contact_array[person][1] + " " +
                       person + " " + contact_array[person][0])
    listbox.pack(side=LEFT, fill=BOTH, expand=1)


def contacts_connect(item):
    """Establish a connection between two contacts."""
    Client(item[1], int(item[2])).start()


def contacts_remove(item, listbox):
    """Remove a contact."""
    if listbox.size() != 0:
        writeSucces("Contact '" + item[1] + "' verwijderd.", "userMain")
        listbox.delete(ACTIVE)
        global contact_array
        h = contact_array.pop(item[1])


def contacts_add(listbox, master):
    """Add a contact."""
    aWindow = Toplevel(master)
    aWindow.title("Contact toevoegen")
    Label(aWindow, text="Naam:").grid(row=0)
    name = Entry(aWindow)
    name.focus_set()
    name.grid(row=0, column=1)
    Label(aWindow, text="IP-adres:").grid(row=1)
    ip = Entry(aWindow)
    ip.grid(row=1, column=1)
    Label(aWindow, text="Poort:").grid(row=2)
    port = Entry(aWindow)
    port.grid(row=2, column=1)
    go = Button(aWindow, text="Voeg toe", command=lambda:
    contacts_add_helper(name.get(), ip.get(), port.get(),
                        aWindow, listbox))
    go.grid(row=3, column=1)


def contacts_add_helper(username, ip, port, window, listbox):
    """Contact adding helper function. Recognizes invalid usernames and
    adds contact to listbox and contact_array.

    """
    for letter in username:
        if letter == " " or letter == "\n":
            writeWarn("Ongeldige naam. Geen spaties!", "userMain")
            return
    if options_sanitation(port, ip):
        listbox.insert(END, username + " " + ip + " " + port)
        contact_array[ip] = [port, username]
        window.destroy()
        return


def load_contacts():
    """Loads the recent chats out of the persistent file contacts.dat."""
    global contact_array
    try:
        filehandle = open("data\\contacts.dat", "r")
    except IOError:
        return
    line = filehandle.readline()
    while len(line) != 0:
        temp = (line.rstrip('\n')).split(" ")  # format: ip, port, name
        contact_array[temp[0]] = temp[1:]
        line = filehandle.readline()
    filehandle.close()


def dump_contacts():
    """Saves the recent chats to the persistent file contacts.dat."""
    global contact_array
    try:
        filehandle = open("data\\contacts.dat", "w")
    except IOError:
        raise IOError("Kan contacten niet opslaan.")
    for contact in contact_array:
        filehandle.write(
            contact + " " + str(contact_array[contact][0]) + " " +
            contact_array[contact][1] + "\n")
    filehandle.close()


def SendText(text):
    for person in conn_array:
        netSend(person, secret_array[person], text)


def hex_to_int(a=str):
    b = {"0":0, "1":1, "2":2, "3":3, "4":4, "5":5, "6":6, "7":7, "8":8, "9":9, "a":10, "b":11, "c":12, "d":13, "e":14, "f":15}
    j = 0
    for i in range(0, len(a)):
        c = a[i]
        d = b[c]
        if d == 0 and i > 0:
            j += 15*16**i
        else:
            j += d*(16**i)
    return j


def tkcolor_to_int(a="#012345"):
    return hex_to_int(a[1:3]) + hex_to_int(a[3:5]) + hex_to_int(a[5:7])



# -----------------------------------------------------------------------------

# places the text from the text bar on to the screen and sends it to
# everyone this program is connected to
def writeToServer(send=True, text=""):
    """Places the text from the text bar on to the screen and sends it to
    everyone this program is connected to.

    """
    global conn_array
    global secret_array
    global username
    global usercolor
    if 1:
        if text.find("*Error") != -1:
            writeError(text[text.find(" text=") + 6:],
                       text[text.find(';') + 1 + 7 + len("username="):text.find(' text=')])
        elif text.find("*Warn") != -1:
            writeWarn(text[text.find(" text=") + 6:],
                      text[text.find(';') + 1 + 6 + len("username="):text.find(' text=')])
        elif text.find("*Info") != -1:
            writeInfo(text[text.find(" text=") + 6:],
                      text[text.find(';') + 1 + 6 + len("username="):text.find(' text=')])
        elif text.find("*Succes") != -1:
            writeSucces(text[text.find(" text=") + 6:],
                        text[text.find(';') + 1 + 8 + len("username="):text.find(' text=')])
        else:
            if tkcolor_to_int(usercolor) > 741:
                writeToScreen('black', usercolor, text[text.find(';') + 1:], username)
            else:
                writeToScreen('white', usercolor, text[text.find(';') + 1:], username)
    if send:
        SendText(text)


#############################

def writeToScreen(fg='white', bg="black", text="", username=""):
    """Places text to main text body in format "[username]: text".
The "color" is for the background"""
    global main_body_text
    global colorNr
    global colNr
    global max_len
    if not isCLI:
        main_body_text.config(state=NORMAL)
        for i in range(0, len("[" + username + "]: " + text), max_len):
            textB = text[i:i + (max_len - len("[" + username + "]: "))]
            main_body_text.insert(END, "[" + username + "]: ")

            main_body_text.insert(END, textB)
            dat = ""
            for i in range(0, max_len - len("[" + username + "]: " + textB)):
                dat = dat + " "
            main_body_text.insert(END, dat)
            main_body_text.tag_add("color" + str(colorNr), "1." + str(colNr), "1." + str(colNr + max_len))
            main_body_text.tag_config("color" + str(colorNr), foreground=fg, background=bg, font=("Courier New", 11))
            colNr += max_len
            colorNr += 1
        main_body_text.yview(END)
        main_body_text.config(state=DISABLED)
    else:
        for i in range(0, len("[" + username + "]: " + text), max_len):
            textB = text[i:i + (max_len - len("[" + username + "]: "))]
            print("[" + username + "]: ", end="")

            print(textB)

#############################
def writeError(text='', username=''):
    """Write a error to the screen the "red" color"""
    writeToScreen('white', 'red', text, username)


def writeWarn(text='', username=''):
    """Write a warning to the screen the "orange" color"""
    writeToScreen('white', 'orange', text, username)


def writeInfo(text='', username=''):
    """Write a info to the screen the "blue" color"""
    writeToScreen('white', 'blue', text, username)


def writeSucces(text='', username=''):
    """Write a succes to the screen the "green" color"""
    writeToScreen('white', 'green', text, username)


def writeChat(text='', username=''):
    """Write a succes to the screen the "darkcyan" color"""
    writeToScreen('white', 'darkcyan', text, username)


def processUserText(event):
    """Takes text from text bar input and calls processUserCommands if it
    begins with '/'.

    """
    data = text_input.get()
    if data[0] != "/":  # is not a command
        writeToServer(True, '#' + usercolor + ';' + data)
    else:
        if data.find(" ") == -1:
            command = data[1:]
        else:
            command = data[1:data.find(" ")]
        params = data[data.find(" ") + 1:].split(" ")
        processUserCommands(command, params)
    text_input.delete(0, END)


def processUserInput(text):
    """ClI version of processUserText."""
    if text[0] != "/":
        writeToServer(True, '#' + usercolor + ';' + text)
    else:
        if text.find(" ") == -1:
            command = text[1:]
        else:
            command = text[1:text.find(" ")]
        params = text[text.find(" ") + 1:].split(" ")
        processUserCommands(command, params)


def set_color():
    global usercolor
    global colorlist
    color = colorchooser.askcolor()
    colorlist = color[0]
    usercolor = color[1]


# -------------------------------------------------------------------------

class Server(threading.Thread):
    "A class for a Server instance."""

    def __init__(self, port):
        threading.Thread.__init__(self)
        self.port = port

    def run(self):
        while True:
            global conn_array
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.bind(('', self.port))

            if len(conn_array) == 0:
                writeSucces("Internet verbinding is goed, wachten op verbindingen op poort: " +
                            str(self.port), "server")
            s.listen(1)
            global conn_init
            conn_init, addr_init = s.accept()
            serv = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            serv.bind(('', 0))  # get a random empty port
            serv.listen(1)

            portVal = str(serv.getsockname()[1])
            if len(portVal) == 5:
                conn_init.send(portVal.encode())
            else:
                conn_init.send(("0" + portVal).encode())

            conn_init.close()
            conn, addr = serv.accept()
            conn_array.append(conn)  # add an array entry for this connection
            writeSucces("Verbonden bij " + str(addr[0]), "server")

            global statusConnect
            if not isCLI:
                statusConnect.set("Verbinding verbreken")
                connecter.config(state=NORMAL)

            # create the numbers for my encryption
            prime = RandomInt(1000, 9000)
            while not isPrime(prime):
                prime = RandomInt(1000, 9000)
            base = RandomInt(20, 100)
            a = RandomInt(20, 100)

            # send the numbers (base, prime, A)
            conn.send(formatNumber(len(str(base))).encode())
            conn.send(str(base).encode())

            conn.send(formatNumber(len(str(prime))).encode())
            conn.send(str(prime).encode())

            conn.send(formatNumber(len(str(pow(base, a) % prime))).encode())
            conn.send(str(pow(base, a) % prime).encode())

            # get B
            data = conn.recv(4)
            data = conn.recv(int(data.decode()))
            b = int(data.decode())

            # calculate the encryption key
            global secret_array
            secret = pow(b, a) % prime
            # store the encryption key by the connection
            secret_array[conn] = secret

            conn.send(formatNumber(len(username)).encode())
            conn.send(username.encode())

            data = conn.recv(4)
            data = conn.recv(int(data.decode()))
            if data.decode() != "Ik":
                username_array[conn] = data.decode()
                contact_array[str(addr[0])] = [str(self.port), data.decode()]
            else:
                username_array[conn] = addr[0]
                contact_array[str(addr[0])] = [str(self.port), "No_nick"]

            passFriends(conn)
            threading.Thread(target=runner, args=(conn, secret)).start()
            # Server(self.port).start()
        # self.start()


# Client chat
class Client(threading.Thread):
    """A class for a Client instance."""

    def __init__(self, host, port):
        threading.Thread.__init__(self)
        self.port = port
        self.host = host

    def run(self):
        global conn_array
        global secret_array
        conn_init2 = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        conn_init2.settimeout(5.0)
        try:
            conn_init2.connect((self.host, self.port))
        except socket.timeout:
            writeError("Timeout-melding. Host is mogelijk niet hier.", "client")
            connecter.config(state=NORMAL)
            raise SystemExit(0)
        except socket.error:
            writeError("Connectie melding. Host heeft net de verbinding geweigerd.", "server")
            connecter.config(state=NORMAL)
            raise SystemExit(0)
        porta = conn_init2.recv(5)
        porte = int(porta.decode())
        conn_init2.close()
        conn = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        conn.connect((self.host, porte))

        writeSucces("Verbonden met: " + self.host +
                    " op poort: " + str(porte), "server")

        global statusConnect
        statusConnect.set("Verbinding verbreken")
        connecter.config(state=NORMAL)

        conn_array.append(conn)
        # get my base, prime, and A values
        data = conn.recv(4)
        data = conn.recv(int(data.decode()))
        base = int(data.decode())
        data = conn.recv(4)
        data = conn.recv(int(data.decode()))
        prime = int(data.decode())
        data = conn.recv(4)
        data = conn.recv(int(data.decode()))
        a = int(data.decode())
        b = RandomInt(20, 100)
        # send the B value
        conn.send(formatNumber(len(str(pow(base, b) % prime))).encode())
        conn.send(str(pow(base, b) % prime).encode())
        secret = pow(a, b) % prime
        secret_array[conn] = secret

        conn.send(formatNumber(len(username)).encode())
        conn.send(username.encode())

        data = conn.recv(4)
        data = conn.recv(int(data.decode()))
        if data.decode() != "Ik":
            username_array[conn] = data.decode()
            contact_array[
                conn.getpeername()[0]] = [str(self.port), data.decode()]
        else:
            username_array[conn] = self.host
            contact_array[conn.getpeername()[0]] = [str(self.port), "No_nick"]
        threading.Thread(target=runner, args=(conn, secret)).start()
        # Server(self.port).start()                             # Errored command! #
        # THIS IS GOOD, BUT I CAN'T TEST ON ONE MACHINE


# Runner voor de chat input
def runner(conn, secret):
    global username_array
    # black_colors = ['cyan', 'turquoise', 'cyan', 'pink', 'yellow', 'white', 'lightGray']
    while 1:
        data = netCatch(conn, secret)
        print(data)
        if data != 1:
            if data.find("*Error") != -1:
                writeToScreen('white', "red",
                              data[data.find(" text=") + 6:],
                              data[data.find(';') + 1 + 7 + len("username="):data.find(' text=')])
            elif data.find("*Warn") != -1:
                writeToScreen('white', "orange",
                              data[data.find(" text=") + 6:],
                              data[data.find(';') + 1 + 6 + len("username="):data.find(' text=')])
            elif data.find("*Info") != -1:
                writeToScreen('white', "blue",
                              data[data.find(" text=") + 6:],
                              data[data.find(';') + 1 + 6 + len("username="):data.find(' text=')])
            elif data.find("*Succes") != -1:
                writeToScreen('white', "green",
                              data[data.find(" text=") + 6:],
                              data[data.find(';') + 1 + 8 + len("username="):data.find(' text=')])
            else:
                usercolor2 = data[data.find('#') + 1:data.find(';')].lower()
                if tkcolor_to_int(usercolor2) > 741:
                    writeToScreen('black', usercolor2, data[data.find(';') + 1:], username_array[conn])
                else:
                    writeToScreen('white', usercolor2, data[data.find(';') + 1:], username_array[conn])
                # if black_colors.count(usercolor) != 0:
                #     writeToScreen('black', usercolor2, data[data.find(';') + 1:], username_array[conn])
                # elif usercolor2.find('##') != -1:
                #     if usercolor2 < '#500000':
                #         writeToScreen('black', usercolor2, data[data.find(';') + 1:], username_array[conn])
                #     else:
                #         writeToScreen('white', usercolor2, data[data.find(';') + 1:], username_array[conn])
                # else:
                #     writeToScreen('white', usercolor2, data[data.find(';') + 1:], username_array[conn])


# -------------------------------------------------------------------------
# Menu helpers

def quick_client():
    """Menu window for connection options."""
    window = Toplevel(root)
    window.title("Verbindings opties")
    window.grab_set()
    Label(window, text="Server IP:").grid(row=0)
    destination = Entry(window)
    destination.grid(row=0, column=1)
    go = Button(window, text="Verbind", command=lambda:
    client_options_go(destination.get(), "9999", window))
    go.grid(row=1, column=1)


# Snelstart een server
def quick_server():
    """Quickstarts a server."""
    Server(9999).start()


# Opslaan geschiedenis
def save_history():
    """Opslaan geschiedenis met Tkinter's asksaveasfilename dialog."""
    global main_body_text
    file_name = asksaveasfilename(
        title="Kies sla-op locatie",
        filetypes=[('Textdocument', '*.txt'), ('Log-document', '*.log'), ('Andere bestanden', '*.*')])
    try:
        filehandle = open(file_name + ".txt", "w")
    except IOError:
        print("Kan geschiedenis niet opslaan")
        writeToScreen('white', 'Red', 'Kan geschiedenis niet opslaan', 'Error')
        return
    contents = main_body_text.get(1.0, END)
    for line in contents:
        filehandle.write(line)
    filehandle.close()


def connects(client_type):
    global conn_array
    connecter.config(state=DISABLED)
    if len(conn_array) == 0:
        if client_type == 0:
            client_options_window(root)
        if client_type == 1:
            server_options_window(root)
    else:
        # connecter.config(state=NORMAL)
        for connection in conn_array:
            connection.send("-001".encode())
        processFlag("-001")


# Signle-chat
def to_one():
    global clientType
    clientType = 0


# Multi-chat
def to_two():
    global clientType
    clientType = 1


# -------------------------------------------------------------------------


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "-cli":
        print("Beginen commando-lijn chat")

    else:
        # Maakt venster
        root = Tk()
        root.title(titleText + " " + chatVersion)

        # Maakt menubar
        menubar = Menu(root)

        # Bestand menu
        file_menu = Menu(menubar, tearoff=0)
        file_menu.add_command(label="Sla chat op", command=lambda: save_history())
        file_menu.add_command(label="Verander naam",
                              command=lambda: username_options_window(root))
        file_menu.add_command(label="Verander kleur", command=lambda: set_color())
        file_menu.add_command(label="Sluit af", command=lambda: root.destroy())
        menubar.add_cascade(label="Bestand", menu=file_menu)

        # Verbind menu
        connection_menu = Menu(menubar, tearoff=0)
        connection_menu.add_command(label="Snel verbinden", command=quick_client)
        connection_menu.add_command(
            label="Verbind met poort", command=lambda: client_options_window(root))
        connection_menu.add_command(
            label="Verbinding verbreken", command=lambda: processFlag("-001"))
        menubar.add_cascade(label="Verbind", menu=connection_menu)
        # Server menu
        server_menu = Menu(menubar, tearoff=0)
        server_menu.add_command(label="Lanceer server", command=quick_server)
        server_menu.add_command(label="Lanceer server-poort",
                                command=lambda: server_options_window(root))
        menubar.add_cascade(label="Server", menu=server_menu)

        menubar.add_command(label="Contacten", command=lambda:
                            contacts_window(root))

        root.config(menu=menubar)

        main_body = Frame(root, height=120, width=50)

        # Globals van kleur
        colorNr = 2
        colNr = 0

        # Global input voor scherm grote
        # scrn_size = input('Scherm grote: ')
        main_body_text = Text(main_body, height=40, width=114)
        # elif scrn_size == '1920x1080':
        #     main_body_text = Text(main_body, height=55, width=114)
        # else:
        #     main_body_text = Text(main_body, width=114)

        # Chat text frame
        body_text_scroll = Scrollbar(main_body)
        main_body_text.focus_set()
        body_text_scroll.pack(side=RIGHT, fill=Y)
        main_body_text.pack(side=LEFT, fill=Y)
        body_text_scroll.config(command=main_body_text.yview)
        main_body_text.config(yscrollcommand=body_text_scroll.set)
        main_body.pack()

        # Welkom bericht
        if welcomeSign:
            writeToScreen('white', "black", "Welkom op de chat programma!", "")

        # Zet de text frame uit
        main_body_text.config(state=DISABLED)

        # Maakt de text-input
        text_input = Entry(root, width=114)
        text_input.bind("<Return>", processUserText)
        text_input.pack()
        text_input.focus_set()

        # Maakr een status voor de connectie
        statusConnect = StringVar()
        statusConnect.set("Lanceer server")
        clientType = 1
        # Status-radioknop:
        Radiobutton(root, text="Client", variable=clientType,
                    value=0, command=to_one).pack(anchor=E)
        Radiobutton(root, text="Server", variable=clientType,
                    value=1, command=to_two).pack(anchor=E)
        connecter = Button(root, textvariable=statusConnect,
                           command=lambda: connects(clientType))
        connecter.pack()

        # Stelt de kleur in

        # Laad contacten
        load_contacts()

        # ------------------------------------------------------------#

        # MAIN-LOOP
        root.mainloop()

        # Slaat de contacten op
        dump_contacts()


while True:
    try:
        port = int(input("port: "))
        if port > 65535 or port < 0:
            print("ERROR: Port number must be between 0 and 65535!")
        break
    except:
        print("ERROR: Invalid port!")

Server(port).start()