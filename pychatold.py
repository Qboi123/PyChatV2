# Importeren sys module
import colorsys
import os
import sys
import threading
import socket
import math
from random import randint

# Versie checken.
from typing import Type, List, Dict, Union, Optional

import nzt

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

# Contact Array
contact_array = dict()  # key: ip address as a string, value: [port, user_name]
max_len = 102

# Sets username and color
user_name = os.getlogin()
user_color = "#007f7f"
color_list = ()

# Server variables setup
location = 0
port = 0
top = ""

# Startup settings
welcomeSign = False
titleText = "Py Chat"
chatVersion = "v2.1"
welcome_message = "Welcome to the PyChat chat application"

main_body_text = 0


class OptionsWindow(Toplevel):
    def __init__(self, master: Tk, title):
        super().__init__(master)
        self.title(title)
        self.minsize(300, 5)
        self.bind_all("<Return>", lambda event: self.go())

        self.grab_set()

    def go(self):
        pass

    def option_delete(self):
        """
        Deletes an option

        :return:
        """

        connecter.config(state=NORMAL)
        self.destroy()

    def error_window(self, texty=""):
        """
        Launches a new window to display the message :param texty:.

        :param texty:
        :return:
        """
        global isCLI
        if isCLI:
            chatText.write_error(texty, "errMain")
        else:
            window = Toplevel(self)
            window.title("ERROR")
            window.grab_set()
            window.minsize(300, 240)
            Label(window, text=texty).pack()
            go = Button(window, text="OK", command=window.destroy)
            go.pack()
            go.focus_set()


class Network(object):
    conn_array: List = []  # stores open sockets
    username_array: Dict = {}  # key: the open sockets in Network.conn_array, value: usernames for the connection
    secret_array: Dict = {}  # key: the open sockets in Network.conn_array, value: integers for encryption
    conn_init = None
    
    def __init__(self, chat_text):
        self.chatText = chat_text
    
    @staticmethod
    def bin_word(word):
        """Converts the string into binary."""
        master = ""
        for letter in word:
            temp = bin(ord(letter))[2:]
            while len(temp) < 7:
                temp = '0' + temp
            master = master + temp
        return master
    
    @staticmethod
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
    
    def x_encode(self, string, number):
        """Encrypts the string by the number."""
        return self.xcrypt(self.bin_word(string), bin(number)[2:])
    
    @staticmethod
    def refract(binary):
        """Returns the string representation of the binary.
        Has trouble with spaces.
    
        """
        master = ""
        for x in range(0, int(len(binary) / 7)):
            master += chr(int(binary[x * 7: (x + 1) * 7], 2) + 0)
        return master
    
    @staticmethod
    def format_number(number):
        """Ensures that number is at least length 4 by
        adding extra 0s to the front.
    
        """
        temp = str(number)
        while len(temp) < 4:
            temp = '0' + temp
        return temp
    
    def net_send(self, conn, secret, message):
        """Sends message through the open socket conn with the encryption key
        secret. Sends the length of the incoming message, then sends the actual
        message.
    
        """
        try:
            conn.send(self.format_number(len(self.x_encode(message, secret))).encode())
            conn.send(self.x_encode(message, secret).encode())
        except socket.error:
            if len(Network.conn_array) != 0:
                self.chatText.write_error(
                    "Sending message failed", "server")
                self.process_flag("-001")
    
    def net_catch(self, conn, secret):
        """Receive and return the message through open socket conn, decrypting
        using key secret. If the message length begins with - instead of a number,
        process as a flag and return 1.
    
        """
        try:
            data = conn.recv(4)
            if data.decode()[0] == '-':
                self.process_flag(data.decode(), conn)
                return 1
            data = conn.recv(int(data.decode()))
            return self.refract(self.xcrypt(data.decode(), bin(secret)[2:]))
        except socket.error:
            if len(Network.conn_array) != 0:
                self.chatText.write_error(
                    "Retrieving of a message failed", "server")
            self.process_flag("-001")
    
    def is_prime(self, number):
        """Checks to see if a number is prime."""
        x = 1
        if number == 2 or number == 3:
            return True
        while x < math.sqrt(number):
            x += 1
            if number % x == 0:
                return False
        return True
    
    # noinspection PyGlobalUndefined
    def process_flag(self, number, conn=None):
        """Process the flag corresponding to number, using open socket conn
        if necessary.
    
        """
        global stateConnect
        global isCLI
        t = int(number[1:])
        if t == 1:  # disconnect
            # in the event of single connection being left or if we're just a
            # client
            if len(Network.conn_array) == 1:
                message_window(main_frame, "Connection Lost", "Info")
                dump = Network.conn_array.pop()
                try:
                    dump.close()
                except socket.error:
                    message_window("Connection lost because of bad connection", "Warning")
                if not isCLI:
                    statusConnect.set("Lanceer")
                    connecter.config(state=NORMAL)
                return
    
            if conn is not None:
                self.chatText.write_warn(f"Connection with {conn.getsockname()[0]} lost", "Client")
                Network.conn_array.remove(conn)
                conn.close()
    
        if t == 2:  # user_name change
            name = self.net_catch(conn, Network.secret_array[conn])
            if self.is_username_free(name):
                self.chatText.write_info(
                    f"Gebruiker {Network.username_array[conn]} heeft zijn naam gewijzigd naar: {name}", "server"
                )
                Network.username_array[conn] = name
                ContactsWindow.contact_array[conn.getpeername()[0]] = [conn.getpeername()[1], name]
    
        # passing a friend who this should connect to (I am assuming it will be
        # running on the same port as the other session)
        if t == 4:
            data = conn.recv(4)
            data = conn.recv(int(data.decode()))
            Client(data.decode(),
                   int(ContactsWindow.contact_array[conn.getpeername()[0]][0]), chatText).start()
    
    def process_user_commands(self, command, param):
        """Processes commands passed in via the / text input."""
        global user_name
    
        if command == "nick":  # change nickname
            for letter in param[0]:
                if letter == " " or letter == "\n":
                    if isCLI:
                        message_window(0, "Name can't contain spaces!")
                    else:
                        message_window(main_frame, "Name can't contain spaces!")
                    return
            if self.is_username_free(param[0]):
                chatText.write_succes("Name is changed to: '" + param[0] + "'", "server")
                for conn in Network.conn_array:
                    conn.send("-002".encode())
                    self.net_send(conn, Network.secret_array[conn], param[0])
                user_name = param[0]
            else:
                if isCLI:
                    message_window(0, param[0] + " is already used as name!")
                else:
                    message_window(main_frame, param[0] + " is already used as name!")
        if command == "disconnect":  # disconnects from current connection
            for conn in Network.conn_array:
                conn.send("-001".encode())
            self.process_flag("-001")
        if command == "connect":  # connects to passed in host port
            if options_sanitation(param[1], param[0]):
                Client(param[0], int(param[1]), chatText).start()
        if command == "host":  # starts server on passed in port
            if options_sanitation(param[0]):
                Server(int(param[0]), chatText).start()
    
    def is_username_free(self, name):
        """Checks to see if the user_name name is free for use."""
        for conn in Network.username_array:
            if name == Network.username_array[conn] or name == user_name:
                return False
        return True
    
    def pass_friends(self, conn):
        """Sends conn all of the people currently in Network.conn_array so they can connect
        to them.
    
        """
        for connection in Network.conn_array:
            if conn != connection:
                conn.send("-004".encode())
                conn.send(
                    self.format_number(len(connection.getpeername()[0])).encode())  # pass the ip address
                conn.send(connection.getpeername()[0].encode())
                # conn.send(formatNumber(len(connection.getpeername()[1])).encode()) #pass the port number
                # conn.send(connection.getpeername()[1].encode())


class ClientOptions(OptionsWindow):
    def __init__(self, master: Tk):
        """Launches client options window for getting destination hostname
        and port.
    
        """
        super(ClientOptions, self).__init__(master, "Connection options")
        self.protocol("WM_DELETE_WINDOW", lambda: self.option_delete())
        
        Label(self, text="Server adress:").grid(row=0)
        self.location_ = Entry(self)
        self.location_.grid(row=0, column=1)
        self.location_.focus_set()
        
        Label(self, text="Poort:").grid(row=1)
        self.port_ = Entry(self)
        self.port_.grid(row=1, column=1)
        
        go_btn = Button(self, text="Connect", command=lambda: self.go())
        go_btn.grid(row=2, column=1)
    
    def go(self):
        "Processes the options entered by the user in the client options window."""
        
        port_ = self.port_.get()
        dest = self.location_.get()
        if options_sanitation(port_, dest):
            if not isCLI:
                self.destroy()
            Client(dest, int(port_), chatText).start()
        elif isCLI:
            sys.exit(1)


def client_connect(dest, port_):
    "Processes the options entered by the user in the client options window."""
    if options_sanitation(port_, dest):
        Client(dest, int(port_), chatText).start()
    elif isCLI:
        sys.exit(1)


def options_sanitation(por, loc=""):
    """Checks to make sure the port and destination ip are both valid.
    Launches error windows if there are any issues.

    """
    global main_frame

    if isCLI:
        root = 0
    if not por.isdigit():
        message_window(root, "Enter port \"number\".")
        return False
    if int(por) < 0 or 65555 < int(por):
        message_window(root, "A port number is a number between 0 and 65535")
        return False
    if loc != "":
        if not ip_process(loc.split(".")):
            message_window(root, "Enter a correct ip please. Such as 127.0.0.1")
            return False
    return True


def ip_process(ip_array):
    """Checks to make sure every section of the ip is a valid number."""
    if len(ip_array) != 4:
        return False
    for ip in ip_array:
        if not ip.isdigit():
            return False
        t = int(ip)
        if t < 0 or 255 < t:
            return False
    return True


# ------------------------------------------------------------------------------

class ServerOptions(OptionsWindow):
    def __init__(self, master: Tk):
        """
        Launches server options window for getting port.

        :param master:
        :return:
        """

        chat_text = chatText
        super().__init__(master, "Connection options")
        self.protocol("WM_DELETE_WINDOW", lambda: self.option_delete())

        Label(self, text="Port:").grid(row=0)
        self.portNumber = Entry(self)
        self.portNumber.grid(row=0, column=1)
        self.portNumber.focus_set()

        go_btn = Button(self, text="Launch",
                        command=lambda: self.go())
        go_btn.grid(row=1, column=1)
        
        self.chatText = chat_text

    def go(self):
        """
        Processes the options entered by the user in the
        server options window.

        :return:
        """

        if options_sanitation(self.portNumber.get()):
            if not isCLI:
                self.destroy()
            Server(int(self.portNumber.get()), self.chatText).start()
        elif isCLI:
            sys.exit(1)


# -------------------------------------------------------------------------

class UsernameOptions(OptionsWindow):
    def __init__(self, master: Tk, network: Network):
        """
        Launches user_name options window for setting user_name.

        :param master:
        :return:
        """
        super().__init__(master, "User options")

        go_btn = Button(self, text="Change", command=lambda: self.go())
        go_btn.pack(side=BOTTOM)

        Label(self, text="Name:").pack(side=LEFT)
        self.userName = Entry(self)
        self.userName.focus_set()
        self.userName.pack(side=LEFT, fill=X, expand=True)
        
        self.network = network

    def go(self, name: str = None):
        """
        Processes the options entered by the user in the
        server options window.

        :param name:
        :return:
        """
        if not name:
            name = self.userName.get()

        self.network.process_user_commands("nick", [name])
        self.destroy()


# -------------------------------------------------------------------------

def message_window(master, texty="", title="ERROR"):
    """
    Launches a new window to display the message :param texty:.

    :param master:
    :param texty:
    :return:
    """
    global isCLI
    if isCLI:
        chatText.write_error(texty, "errMain")
    else:
        window = Toplevel(master)
        window.title(title)
        window.grab_set()
        window.minsize(300, 240)

        Label(window, text=texty).pack()
        go = Button(window, text="OK", command=window.destroy)
        go.pack()
        go.focus_set()
        
        
class MessageWindow(object):
    def __init__(self, master: Optional[Union[Tk, Toplevel]] = None, texty: str = "", title: str = "Error"):
        if master:
            self.window = Toplevel(master)
        else:
            self.window = Tk()
        
        self.window.title(title)
        self.window.grab_set()
        self.window.minsize(300, 240)

        Label(self.window, text=texty).pack(TOP)
        ok_button = Button(self.window, text="OK", command=self.window.destroy)
        ok_button.pack(BOTTOM)
        ok_button.focus_set()
        
    def destroy(self):
        self.window.destroy()


def option_delete(window: Toplevel):
    """
    Deletes an option

    :param window:
    :return:
    """
    connecter.config(state=NORMAL)
    window.destroy()


def send_text(text: str, network: Network = None):
    """
    Sends text to the clients

    :param text:
    :return:
    """
    
    if not network:
        network = Network(chatText)
    
    for person in Network.conn_array:
        network.net_send(person, Network.secret_array[person], text)


class ColorHexInt(object):
    @staticmethod
    def hex_to_int(a=Type[str]):
        """
        Hexadecimal to integer.
    
        :param a:
        :return:
        """
        b = {"0": 0, "1": 1, "2": 2, "3": 3, "4": 4, "5": 5, "6": 6, "7": 7, "8": 8, "9": 9, "a": 10, "b": 11, "c": 12,
             "d": 13, "e": 14, "f": 15}
        j = 0
        for i in range(0, len(a)):
            c = a[i]
            d = b[c]
            if d == 0 and i > 0:
                j += 15 * 16 ** i
            else:
                j += d * (16 ** i)
        return j

    @staticmethod
    def tkcolor_to_int(hex_="#012345"):
        """
    
        :param hex_:
        :return:
        """
        return ColorHexInt.hex_to_int(hex_[1:3]) + ColorHexInt.hex_to_int(hex_[3:5]) + ColorHexInt.hex_to_int(hex_[5:7])


# -------------------------------------------------------------------------
# Menu helpers

class QuickNetwork(object):        
    @staticmethod
    def quick_client():
        """
        Menu window for connection options.
    
        :return:
        """
    
        global main_frame
    
        window = OptionsWindow(root, "Verbindings opties")
        
        Label(window, text="Server IP:").grid(row=0)
        destination = Entry(window)
        destination.grid(row=0, column=1)

        window.go = lambda: client_connect(destination.get(), "9999")
        go = Button(window, text="Verbind", command=window.go)
        go.grid(row=1, column=1)
    

    @staticmethod
    def quick_server():
        """
        Quick-starts a server.
    
        :return:
        """
    
        server = Server(9999, chatText)
        server.start()
        return server


def save_history(tk_text: Text):
    """
    Save history with Tkinter's "asksavefilename" dialog.

    :type tk_text: tkinter.Text
    :return:
    """
    
    filename = asksaveasfilename(
        title="Save history as...",
        filetypes=[('Text document', '*.txt'), ('Log file', '*.log'), ('Other files', '*.*')])
    try:
        with open(filename + ".txt", "w+") as file:
            contents = tk_text.get(1.0, END)
            file.write(contents)
            file.close()
    except IOError as e:
        if "file" in locals():
            MessageWindow(main_frame, f"Can't save history\nIOErrror: {e.__str__()}")
            return
        MessageWindow(main_frame, "Can't save history")
    except Exception as e:
        MessageWindow(main_frame, f"Internal error when saving history\n{e.__class__.__name__}: {e.__str__()}")


class ClientType(object):
    clientType = 0
    
    @staticmethod
    def connects(client_type, network: Network):
        """
        Choose what client type, to choose the options of.
    
        :param client_type:
        :return:
        """
    
        connecter.config(state=DISABLED)
        if len(Network.conn_array) == 0:
            if client_type == 0:
                ClientOptions(main_frame)
            if client_type == 1:
                ServerOptions(main_frame)
        else:
            connecter.config(state=NORMAL)
            for connection in Network.conn_array:
                connection.send("-001".encode())
            network.process_flag("-001")
    
    @staticmethod
    def to_one():
        """
        Client chat
    
        :return:
        """
    
        ClientType.clientType = 0
    
    @staticmethod
    def to_two():
        """
        Server chat
    
        :return:
        """
        
        ClientType.clientType = 1


class ContactsWindow(Toplevel):
    contact_array = {}

    def __init__(self, master: Tk):
        """
        Displays the contacts window, allowing the user to select a recent
        connection to reuse.
    
        :param master:
        :return:
        """
        global contact_array
        super(ContactsWindow, self).__init__(master)
        self.title("Contacts")
        self.grab_set()
        scrollbar = Scrollbar(self, orient=VERTICAL)
        self.listbox = Listbox(self, yscrollcommand=scrollbar.set)
        scrollbar.config(command=self.listbox.yview)
        scrollbar.pack(side=RIGHT, fill=Y)
        buttons = Frame(self)
        c_but = Button(buttons, text="Connect", command=lambda: self.contacts_connect())
        c_but.pack(side=LEFT)
        d_but = Button(buttons, text="Delete",
                       command=lambda: self.contacts_remove(
                       ))
        d_but.pack(side=LEFT)
        a_but = Button(buttons, text="Add",
                       command=lambda: self.contacts_add())
        a_but.pack(side=LEFT)
        buttons.pack(side=BOTTOM)
    
        for person in contact_array:
            self.listbox.insert(END, contact_array[person][1] + " " +
                           person + " " + contact_array[person][0])
        self.listbox.pack(side=LEFT, fill=BOTH, expand=1)
    
    
    def contacts_connect(self):
        """
        Establish a connection between two contacts.
    
        :return:
        """
        item = self.listbox.get(ACTIVE).split(" ")
        
        Client(item[1], int(item[2]), chatText).start()
    
    def contacts_remove(self):
        """
        Remove a contact.
    
        :return:
        """
        item = self.listbox.get(ACTIVE).split(" ")
        
        if self.listbox.size() != 0:
            chatText.write_succes("Contact '" + item[1] + "' deleted.", "userMain")
            self.listbox.delete(ACTIVE)
            global contact_array
    
    def contacts_add(self):
        """
        Add a contact.
    
        :return:
        """
        
        a_window = Toplevel(self)
        a_window.title("Add contact")
        Label(a_window, text="Name:").grid(row=0)
        name = Entry(a_window)
        name.focus_set()
        name.grid(row=0, column=1)
        Label(a_window, text="IP:").grid(row=1)
        ip = Entry(a_window)
        ip.grid(row=1, column=1)
        Label(a_window, text="Port:").grid(row=2)
        port_ = Entry(a_window)
        port_.grid(row=2, column=1)
        go = Button(a_window, text="Add",
                    command=lambda: self.contacts_add_helper(name.get(), ip.get(), port_.get(), a_window)
                    )
        go.grid(row=3, column=1)
    
    
    def contacts_add_helper(self, username: str, ip: str, port_: str, window: Toplevel):
        """
        Contact adding helper function. Recognizes invalid username's and
        adds contact to listbox and contact_array.
    
        :param username:
        :param ip:
        :param port_:
        :param window:
        :param listbox:
        :return:
        """
        if (" " in username) or ("\n" in username):
            MessageWindow(window, "Username can't contain spaces or newlines")
            return
        if options_sanitation(port_, ip):
            self.listbox.insert(END, username + " " + ip + " " + port_)
            contact_array[ip] = [port_, username]
            window.destroy()
            return


def load_data():
    """
    Loads the recent chats out of the persistent file contacts.dat.

    :return:
    """

    global contact_array
    global user_color
    global user_name
    global welcome_message

    try:
        file = nzt.NZTFile("data/data.nzt", "r")
        file.load()
        data = file.data
        file.close()
    except FileNotFoundError:
        user_name = os.getlogin()
        chatText.write_succes(welcome_message, "System")
        return

    contact_array = data["Contacts"]
    user_color = data["User"]["color"]
    user_name = data["User"]["name"]


def dump_data():
    """
    Saves the recent chats to the persistent file contacts.dat.

    :return:
    """
    global contact_array
    if not os.path.exists("data/"):
        os.makedirs("data/")

    file = nzt.NZTFile("data/data.nzt", "w")
    file.data = {
        "Contacts": contact_array,
        "User": {
            "color": user_color,
            "name": user_name
        }
    }
    file.save()
    file.close()


class ChatText(object):
    def __init__(self):
        self.userName = property(lambda: user_name)
        self.userColor = property(lambda: user_color)
        self.rowNumber = 0
        self.colorNumber = 2

    def write2server(self, send=True, text=""):
        """
        Places the text from the text bar on to the screen and sends it to
        everyone this program is connected to.

        :param send:
        :param text:
        :return:
        """

        if 1:
            if text.find("*Error") != -1:
                self.write_error(text[text.find(" text=") + 6:],
                                 text[text.find(';') + 1 + 7 + len("user_name="):text.find(' text=')])
            elif text.find("*Warn") != -1:
                self.write_warn(text[text.find(" text=") + 6:],
                                text[text.find(';') + 1 + 6 + len("user_name="):text.find(' text=')])
            elif text.find("*Info") != -1:
                self.write_info(text[text.find(" text=") + 6:],
                                text[text.find(';') + 1 + 6 + len("user_name="):text.find(' text=')])
            elif text.find("*Succes") != -1:
                self.write_succes(text[text.find(" text=") + 6:],
                                  text[text.find(';') + 1 + 8 + len("user_name="):text.find(' text=')])
            else:
                if colorsys.rgb_to_hsv(eval("0x" + user_color[0:2]) / 255,
                                       eval("0x" + user_color[2:4]) / 255,
                                       eval("0x" + user_color[4:6]) / 255)[2] >= 0.5:
                    self.write2screen('black', self.userColor, text[text.find(';') + 1:], self.userName)
                else:
                    self.write2screen('white', self.userColor, text[text.find(';') + 1:], self.userName)
        if send:
            send_text(text)

    def write2screen(self, fg='white', bg="black", text="", username=""):
        """
        Places text to main text body in format "[user_name]: text".
        The "color" is for the background

        :param fg:
        :param bg:
        :param text:
        :param username:
        :return:
        """

        global main_body_text
        global max_len
        if not isCLI:
            main_body_text.config(state=NORMAL)
            text_b = text

            main_body_text.insert(END, "[" + username + "]: ")
            main_body_text.insert(END, text_b + "\n")

            self.rowNumber += 1
            main_body_text.tag_add("color" + str(self.colorNumber), str(self.rowNumber) + ".0",
                                   str(self.rowNumber + 1) + ".0")  # +str(len(text)+len("[" + user_name + "]: ")+2))
            main_body_text.tag_config("color" + str(self.colorNumber), foreground=fg, background=bg,
                                      font=("Courier New", 11))
            self.colorNumber += 1

            main_body_text.yview(END)
            main_body_text.config(state=DISABLED)
        else:
            for i in range(0, len("[" + username + "]: " + text), max_len):
                text_b = text[i:i + (max_len - len("[" + username + "]: "))]
                print("[" + username + "]: ", end="")

                print(text_b)

    def write_error(self, text='', username=''):
        """
        Write a error to the screen the "red" color

        :param text:
        :param username:
        :return:
        """
        self.write2screen('white', 'red', text, username)

    def write_warn(self, text='', username=''):
        """
        Write a warning to the screen the "orange" color"

        :param text:
        :param username:
        :return:
        """
        self.write2screen('white', 'orange', text, username)

    def write_info(self, text: str = '', username: str = ''):
        """
        Write a info to the screen the "cyan" color

        :param text:
        :param username:
        :return:
        """
        self.write2screen('white', 'cyan', text, username)

    def write_succes(self, text: str = '', username: str = ''):
        """Write a succes to the screen the "green" color"""
        self.write2screen('white', 'green', text, username)

    def write_chat(self, text: str = '', username: str = ''):
        """Write a succes to the screen the "darkcyan" color"""
        self.write2screen('white', 'darkcyan', text, username)


# places the text from the text bar on to the screen and sends it to
# everyone this program is connected to


#############################

#############################


# noinspection PyUnusedLocal
def process_user_text(event: Event, network: Network):
    """Takes text from text bar input and calls processUserCommands if it
    begins with '/'.

    """
    data = text_input.get()
    if data[0] != "/":  # is not a command
        chatText.write2server(True, '#' + user_color + ';' + data)
    else:
        if data.find(" ") == -1:
            command = data[1:]
        else:
            command = data[1:data.find(" ")]
        params = data[data.find(" ") + 1:].split(" ")
        network.process_user_commands(command, params)
    text_input.delete(0, END)


def process_user_input(text: str, network: Network):
    """ClI version of processUserText."""
    if text[0] != "/":
        chatText.write2server(True, '#' + user_color + ';' + text)
    else:
        if text.find(" ") == -1:
            command = text[1:]
        else:
            command = text[1:text.find(" ")]
        params = text[text.find(" ") + 1:].split(" ")
        network.process_user_commands(command, params)


def set_color():
    global user_color
    global color_list
    color = colorchooser.askcolor()
    color_list = color[0]
    user_color = color[1]


class ChatThread(threading.Thread):
    def __init__(self, chat_text, network: Network):
        super(ChatThread, self).__init__()
        self.chatText = chat_text
        self.network = network

    def runner(self, conn, secret):
        """
        Runner for chat input

        :param conn:
        :param secret:
        :return:
        """

        while 1:
            data = self.network.net_catch(conn, secret)
            print("DATA:", data)
            if data != 1:
                if data.find("*Error") != -1:
                    self.chatText.write2screen('white', "red",
                                               data[data.find(" text=") + 6:],
                                               data[data.find(';') + 1 + 7 + len("user_name="):data.find(' text=')])
                elif data.find("*Warn") != -1:
                    self.chatText.write2screen('white', "orange",
                                               data[data.find(" text=") + 6:],
                                               data[data.find(';') + 1 + 6 + len("user_name="):data.find(' text=')])
                elif data.find("*Info") != -1:
                    self.chatText.write2screen('white', "blue",
                                               data[data.find(" text=") + 6:],
                                               data[data.find(';') + 1 + 6 + len("user_name="):data.find(' text=')])
                elif data.find("*Succes") != -1:
                    self.chatText.write2screen('white', "green",
                                               data[data.find(" text=") + 6:],
                                               data[data.find(';') + 1 + 8 + len("user_name="):data.find(' text=')])
                else:
                    user_color2 = data[data.find('#') + 1:data.find(';')].lower()
                    if colorsys.rgb_to_hsv(eval("0x" + user_color[0:2]) / 255,
                                           eval("0x" + user_color[2:4]) / 255,
                                           eval("0x" + user_color[4:6]) / 255)[2] >= 0.5:
                        self.chatText.write2screen('black', user_color2, data[data.find(';') + 1:],
                                                   Network.username_array[conn])
                    else:
                        self.chatText.write2screen('white', user_color2, data[data.find(';') + 1:],
                                                   Network.username_array[conn])


# -------------------------------------------------------------------------
class Server(ChatThread):
    "A class for a Server instance."""

    def __init__(self, port_, chat_text: ChatText, network: Network):
        super(Server, self).__init__(chat_text)
        self.port = port_
        self.chatText = chat_text
        self.network = network

    def run(self):
        while True:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            try:
                s.bind(('', self.port))
            except OSError as e:
                self.chatText.write_error(e.__class__.__name__ + ": " + e.__str__(), "Server")
                return

            if len(Network.conn_array) == 0:
                self.chatText.write_succes("Internet verbinding is goed, wachten op verbindingen op poort: " +
                                           str(self.port), "server")
            s.listen(1)
            global conn_init

            conn_init, addr_init = s.accept()
            serv = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            serv.bind(('', 0))  # get a random empty port_
            serv.listen(1)

            port_val = str(serv.getsockname()[1])
            if len(port_val) == 5:
                conn_init.send(port_val.encode())
            else:
                conn_init.send(("0" + port_val).encode())

            conn_init.close()
            conn, addr = serv.accept()
            Network.conn_array.append(conn)  # add an array entry for this connection
            self.chatText.write_succes("Connected with server " + str(addr[0]))

            global stateConnect
            if not isCLI:
                statusConnect.set("Verbinding verbreken")
                connecter.config(state=NORMAL)

            # create the numbers for my encryption
            prime = randint(1000, 9000)
            while not self.network.is_prime(prime):
                prime = randint(1000, 9000)
            base = randint(20, 100)
            a = randint(20, 100)

            # send the numbers (base, prime, A)
            conn.send(self.ntework.format_number(len(str(base))).encode())
            conn.send(str(base).encode())

            conn.send(self.network.format_number(len(str(prime))).encode())
            conn.send(str(prime).encode())

            conn.send(self.network.format_number(len(str(pow(base, a) % prime))).encode())
            conn.send(str(pow(base, a) % prime).encode())

            # get B
            data = conn.recv(4)
            data = conn.recv(int(data.decode()))
            b = int(data.decode())

            # calculate the encryption key
            secret = pow(b, a) % prime
            # store the encryption key by the connection
            Network.secret_array[conn] = secret

            conn.send(self.network.format_number(len(user_name)).encode())
            conn.send(user_name.encode())

            data = conn.recv(4)
            data = conn.recv(int(data.decode()))
            if data.decode() != "Ik":
                Network.username_array[conn] = data.decode()
                contact_array[str(addr[0])] = [str(self.port), data.decode()]
            else:
                Network.username_array[conn] = addr[0]
                contact_array[str(addr[0])] = [str(self.port), "No_nick"]

            self.network.pass_friends(conn)
            threading.Thread(target=self.runner, args=(conn, secret)).start()
            # Server(self.port_).start()
        # self.start()


# Client chat
class Client(ChatThread):
    """
    A class for a Client instance.
    """

    def __init__(self, host, port_, chat_text):
        """

        :param host:
        :param port_:
        """
        super(Client, self).__init__(chat_text)
        self.port = port_
        self.host = host

    def run(self):
        """

        :return:
        """
        conn_init2 = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        conn_init2.settimeout(5.0)
        try:
            conn_init2.connect((self.host, self.port))
        except socket.timeout:
            self.chatText.write_error("Timeout-melding. Host is mogelijk niet hier.", "client")
            connecter.config(state=NORMAL)
            raise SystemExit(0)
        except socket.error:
            self.chatText.write_error("Connectie melding. Host heeft net de verbinding geweigerd.", "server")
            connecter.config(state=NORMAL)
            raise SystemExit(0)
        porta = conn_init2.recv(5)
        porte = int(porta.decode())
        conn_init2.close()
        conn = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        conn.connect((self.host, porte))

        self.chatText.write_succes("Verbonden met: " + self.host +
                                   " op poort: " + str(porte), "server")

        global stateConnect
        statusConnect.set("Verbinding verbreken")
        connecter.config(state=NORMAL)

        Network.conn_array.append(conn)

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
        b = randint(20, 100)
        # send the B value
        conn.send(format_number(len(str(pow(base, b) % prime))).encode())
        conn.send(str(pow(base, b) % prime).encode())
        secret = pow(a, b) % prime
        Network.secret_array[conn] = secret

        conn.send(format_number(len(user_name)).encode())
        conn.send(user_name.encode())

        data = conn.recv(4)
        data = conn.recv(int(data.decode()))
        if data.decode() != "Ik":
            Network.username_array[conn] = data.decode()
            contact_array[
                conn.getpeername()[0]] = [str(self.port), data.decode()]
        else:
            Network.username_array[conn] = self.host
            contact_array[conn.getpeername()[0]] = [str(self.port), "No_nick"]
        threading.Thread(target=self.runner, args=(conn, secret)).start()
        # Server(self.port_).start()                             # Errored command! #
        # THIS IS GOOD, BUT I CAN'T TEST ON ONE MACHINE


def exit_app():
    dump_data()
    sys.exit()


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "-cli":
        # CommandLine Interface (CLI) chat
        print("Starting Commandline Interface chat")
    else:
        chatText = ChatText()
        # Create window
        main_frame = Tk()
        main_frame.title(titleText + " " + chatVersion)
        main_frame.protocol("WM_DELETE_WINDOW", exit_app)

        # Create menu bar
        menubar = Menu(main_frame)

        # File menu
        file_menu = Menu(menubar, tearoff=0)
        file_menu.add_command(label="Sla chat op", command=lambda: save_history())
        file_menu.add_command(label="Change username",
                              command=lambda: UsernameOptions(main_frame))
        file_menu.add_command(label="Change color", command=lambda: set_color())
        file_menu.add_command(label="Exit", command=lambda: main_frame.destroy())
        menubar.add_cascade(label="File", menu=file_menu)

        # Connection menu
        connection_menu = Menu(menubar, tearoff=0)
        connection_menu.add_command(label="Quick connect", command=quick_client)
        connection_menu.add_command(
            label="Connect with port", command=lambda: client_options_window(main_frame))
        connection_menu.add_command(
            label="Disconnect", command=lambda: process_flag("-001"))
        menubar.add_cascade(label="Connect", menu=connection_menu)
        # Server menu
        server_menu = Menu(menubar, tearoff=0)
        server_menu.add_command(label="Launch server", command=quick_server)
        server_menu.add_command(label="Launch server with port",
                                command=lambda: ServerOptions(main_frame))
        menubar.add_cascade(label="Server", menu=server_menu)

        # Contacts entry
        menubar.add_command(label="Contacts", command=lambda: contacts_window(main_frame))

        # Sets menu bar
        main_frame.config(menu=menubar)

        # Main body
        main_body = Frame(main_frame, height=120, width=50)
        main_body_text = Text(main_body, height=40, width=114)

        body_text_scroll = Scrollbar(main_body)
        main_body_text.focus_set()

        body_text_scroll.pack(side=RIGHT, fill=Y)
        main_body_text.pack(side=LEFT, fill=BOTH, expand=True)

        body_text_scroll.config(command=main_body_text.yview)
        main_body_text.config(yscrollcommand=body_text_scroll.set)
        main_body.pack(fill=BOTH, expand=True)

        # Disables the chat text (frame)
        main_body_text.config(state=DISABLED)

        # Create chat input
        text_input = Entry(main_frame, width=114)
        text_input.bind("<Return>", process_user_text)
        text_input.pack()
        text_input.focus_set()

        # Create state connection
        stateConnect = StringVar()
        stateConnect.set("Lanceer server")
        clientType = 1

        # Connection state radiobutton:
        Radiobutton(main_frame, text="Client", variable=clientType,
                    value=0, command=to_one).pack(anchor=E)
        Radiobutton(main_frame, text="Server", variable=clientType,
                    value=1, command=to_two).pack(anchor=E)
        connecter = Button(main_frame, textvariable=stateConnect,
                           command=lambda: connects(clientType))
        connecter.pack()

        # Load contacts
        load_data()

        # Welcome message
        if welcomeSign:
            chatText.write2screen('white', "black", f"{user_name}, welcome on the chat application", "")

        # ------------------------------------------------------------#

        # Main loop
        main_frame.mainloop()

        # Saving the data. (If changed of course)
        dump_data()
