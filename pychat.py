import colorsys
import math
import socket
import threading
from tkinter import colorchooser
from tkinter.filedialog import asksaveasfilename
from tkinter.tix import *
from typing import Type, List, Dict, Union, Optional, Tuple

from advUtils.network import PackageEncoder, PackageDecoder, PackageSystem

import nzt

version = sys.version_info.major
subversion = sys.version_info.minor
subsubversion = sys.version_info.micro

if len(sys.argv) > 1 and sys.argv[1] == "-cli":
    print("WARNING: The -cli options is currently experminental, please use gui for better experience.")
    print("Starting commandline chat.")
    isCLI = True
else:
    isCLI = False

if version != 3:  # Show message if on python 2.x or the future release 4.x. (Unknown when older than 2.0.1)
    print("This program is only supported for Python 3.x")
    input()
elif version == 3:
    if subversion != 7:
        print("WARNING: This program is currently written in Python 3.7.4")
        print("         Please use Python 3.7.x")

print(f"Starting program on Python {version}.{subversion}.{subsubversion}")
print(f"Tested Python versions: 3.7.4 and 3.7.6")

# Globals
EVT_DISCONNECT = "disconnect"
EVT_USERNAME_CHANGE = "username_change"
EVT_CONTACT = "contact"

# ---- THEME START ---- # TODO: Remove this, it's overriden with user_color
# Theme Colors
COLOR_ACCENT = "#7f7fff"
COLOR_WIN_BG = "#ffffff"
COLOR_WIN_FG = "#474747"
COLOR_CHAT_BG = "#efefef"
COLOR_CHAT_FG = "#37ff37"
COLOR_TEXT_INPUT_BG = "#efefef"
COLOR_TEXT_INPUT_FG = "#373737"
COLOR_SCROLL_FG = "#afafaf"
COLOR_SCROLL_BG = "#efefef"
COLOR_CLIENT_TYPE_BG = "#efefef"
COLOR_CLIENT_TYPE_FG = "#373737"
COLOR_CLIENT_TYPE_ACT = COLOR_ACCENT
COLOR_CONNECTER_BG = "#efefef"
COLOR_CONNECTER_FG = "#373737"
COLOR_CONNECTER_ACT = COLOR_ACCENT
COLOR_OK_BTN_BG = "#efefef"
COLOR_OK_BTN_FG = "#373737"
COLOR_OK_BTN_ACT = None
COLOR_BTN_BG = "#efefef"
COLOR_BTN_FG = "#373737"
COLOR_BTN_ACT = None
COLOR_LIST_BG = "#efefef"
COLOR_LIST_FG = "#373737"
COLOR_LIST_SEL = COLOR_ACCENT
COLOR_LBL_BG = COLOR_WIN_BG
COLOR_LBL_FG = COLOR_WIN_FG

# Theme Reliefs
RELIEF_WIN = "flat"
RELIEF_CHAT = "flat"
RELIEF_TEXT_INPUT = "flat"
RELIEF_SCROLL = "flat"
RELIEF_CLIENT_TYPE = "flat"
RELIEF_CONNECTER = "flat"
RELIEF_OK_BTN = "flat"
RELIEF_BTN = "flat"
RELIEF_LIST = "flat"
RELIEF_LBL = "flat"

# Theme Border Width's
BORDER_WIN = 0
BORDER_CHAT = 0
BORDER_TEXT_INPUT = 0
BORDER_SCROLL = 0
BORDER_CLIENT_TYPE = 0
BORDER_CONNECTER = 0
BORDER_OK_BTN = 0
BORDER_BTN = 0
BORDER_LIST = 0
BORDER_LBL = 0

THEME_DARK = "theme::dark"
THEME_LIGHT = "theme::light"
COLOR_THEME = THEME_DARK

# ----- THEME END ----- #

# Encryption Salt
SALT: bytes = b"SlTKeYOpHygTYkP3"  # TODO: This is unused

# Contact Array
contact_array: dict = dict()  # key: ip address as a string, value: [port, user_name]
max_len: int = 102  # Unknown uses

# Sets username and color
user_name: str = os.getlogin()  # TODO: Update with message dialog
user_color: str = "#007f7f"
password: Optional[str] = None  # Is set with saved configuration (not incode)
color_list: Union[List, Tuple] = ()  # Color list possible unused

# Server variables setup
location: int = 0  # Unknown uses
port: int = 0  # Unknown uses
top: str = ""  # Unknown uses

# Startup settings
welcomeSign: bool = False  # TODO: Unused
titleText: str = "Py Chat"  # TODO: Update title
chatVersion: str = "v3.0"  # TODO: Update version
welcome_message: str = "Welcome to the PyChat chat application"  # TODO: Usused


# main_body_text: Optional[Text] = None  # TODO: Update to None


def update_theme():
    if COLOR_THEME == THEME_LIGHT:
        update_color_light()  # Theme colors: background, foreground, active, selection
    elif COLOR_THEME == THEME_DARK:
        update_color_dark()
    update_relief()  # Theme reliefs: "flat", "sunken", "raised"
    update_border()  # Theme borders: width, thickness of the border. Is an integer


def update_color_dark():
    global user_color
    global color_list
    global COLOR_ACCENT
    global COLOR_WIN_BG, COLOR_WIN_FG
    global COLOR_CHAT_BG, COLOR_CHAT_FG
    global COLOR_TEXT_INPUT_BG, COLOR_TEXT_INPUT_FG
    global COLOR_SCROLL_BG, COLOR_SCROLL_FG
    global COLOR_CLIENT_TYPE_BG, COLOR_CLIENT_TYPE_FG, COLOR_CLIENT_TYPE_ACT
    global COLOR_CONNECTER_BG, COLOR_CONNECTER_FG, COLOR_CONNECTER_ACT
    global COLOR_OK_BTN_BG, COLOR_OK_BTN_FG, COLOR_OK_BTN_ACT
    global COLOR_BTN_BG, COLOR_BTN_FG, COLOR_BTN_ACT
    global COLOR_LIST_BG, COLOR_LIST_FG, COLOR_LIST_SEL
    global COLOR_LBL_BG, COLOR_LBL_FG

    # Theme Colors
    COLOR_ACCENT = user_color
    COLOR_WIN_BG = "#1f1f1f"
    COLOR_WIN_FG = "#8f8f8f"
    COLOR_CHAT_BG = "#2f2f2f"
    COLOR_CHAT_FG = "#7f7f7f"
    COLOR_TEXT_INPUT_BG = "#2f2f2f"
    COLOR_TEXT_INPUT_FG = "#7f7f7f"
    COLOR_SCROLL_FG = "#3f3f3f"
    COLOR_SCROLL_BG = "#2f2f2f"
    COLOR_CLIENT_TYPE_BG = "#2f2f2f"
    COLOR_CLIENT_TYPE_FG = "#7f7f7f"
    COLOR_CLIENT_TYPE_ACT = COLOR_ACCENT
    COLOR_CONNECTER_BG = "#2f2f2f"
    COLOR_CONNECTER_FG = "#7f7f7f"
    COLOR_CONNECTER_ACT = COLOR_ACCENT
    COLOR_OK_BTN_BG = "#2f2f2f"
    COLOR_OK_BTN_FG = "#7f7f7f"
    COLOR_OK_BTN_ACT = None
    COLOR_BTN_BG = "#2f2f2f"
    COLOR_BTN_FG = "#7f7f7f"
    COLOR_BTN_ACT = None
    COLOR_LIST_BG = "#2f2f2f"
    COLOR_LIST_FG = "#7f7f7f"
    COLOR_LIST_SEL = COLOR_ACCENT
    COLOR_LBL_BG = COLOR_WIN_BG
    COLOR_LBL_FG = COLOR_WIN_FG


def update_color_light():
    global user_color
    global color_list
    global COLOR_ACCENT
    global COLOR_WIN_BG, COLOR_WIN_FG
    global COLOR_CHAT_BG, COLOR_CHAT_FG
    global COLOR_TEXT_INPUT_BG, COLOR_TEXT_INPUT_FG
    global COLOR_SCROLL_BG, COLOR_SCROLL_FG
    global COLOR_CLIENT_TYPE_BG, COLOR_CLIENT_TYPE_FG, COLOR_CLIENT_TYPE_ACT
    global COLOR_CONNECTER_BG, COLOR_CONNECTER_FG, COLOR_CONNECTER_ACT
    global COLOR_OK_BTN_BG, COLOR_OK_BTN_FG, COLOR_OK_BTN_ACT
    global COLOR_BTN_BG, COLOR_BTN_FG, COLOR_BTN_ACT
    global COLOR_LIST_BG, COLOR_LIST_FG, COLOR_LIST_SEL
    global COLOR_LBL_BG, COLOR_LBL_FG

    # Theme Colors
    COLOR_ACCENT = user_color
    COLOR_WIN_BG = "#ffffff"
    COLOR_WIN_FG = "#474747"
    COLOR_CHAT_BG = "#efefef"
    COLOR_CHAT_FG = "#37ff37"
    COLOR_TEXT_INPUT_BG = "#efefef"
    COLOR_TEXT_INPUT_FG = "#373737"
    COLOR_SCROLL_FG = "#afafaf"
    COLOR_SCROLL_BG = "#efefef"
    COLOR_CLIENT_TYPE_BG = "#efefef"
    COLOR_CLIENT_TYPE_FG = "#373737"
    COLOR_CLIENT_TYPE_ACT = COLOR_ACCENT
    COLOR_CONNECTER_BG = "#efefef"
    COLOR_CONNECTER_FG = "#373737"
    COLOR_CONNECTER_ACT = COLOR_ACCENT
    COLOR_OK_BTN_BG = "#efefef"
    COLOR_OK_BTN_FG = "#373737"
    COLOR_OK_BTN_ACT = None
    COLOR_BTN_BG = "#efefef"
    COLOR_BTN_FG = "#373737"
    COLOR_BTN_ACT = None
    COLOR_LIST_BG = "#efefef"
    COLOR_LIST_FG = "#373737"
    COLOR_LIST_SEL = COLOR_ACCENT
    COLOR_LBL_BG = COLOR_WIN_BG
    COLOR_LBL_FG = COLOR_WIN_FG


def update_relief():
    global RELIEF_WIN, RELIEF_CHAT, RELIEF_TEXT_INPUT, RELIEF_SCROLL, RELIEF_CLIENT_TYPE, RELIEF_CONNECTER
    global RELIEF_OK_BTN, RELIEF_BTN, RELIEF_LIST, RELIEF_LBL

    # Theme Reliefs
    RELIEF_WIN = "flat"
    RELIEF_CHAT = "flat"
    RELIEF_TEXT_INPUT = "flat"
    RELIEF_SCROLL = "flat"
    RELIEF_CLIENT_TYPE = "flat"
    RELIEF_CONNECTER = "flat"
    RELIEF_OK_BTN = "flat"
    RELIEF_BTN = "flat"
    RELIEF_LIST = "flat"
    RELIEF_LBL = "flat"


def update_border():
    global BORDER_WIN, BORDER_CHAT, BORDER_TEXT_INPUT, BORDER_SCROLL, BORDER_CLIENT_TYPE, BORDER_CONNECTER
    global BORDER_OK_BTN, BORDER_BTN, BORDER_LIST, BORDER_LBL

    # Theme Border Width's
    BORDER_WIN = 0
    BORDER_CHAT = 0
    BORDER_TEXT_INPUT = 0
    BORDER_SCROLL = 0
    BORDER_CLIENT_TYPE = 0
    BORDER_CONNECTER = 0
    BORDER_OK_BTN = 0
    BORDER_BTN = 0
    BORDER_LIST = 0
    BORDER_LBL = 0


class CryptedPackageSystem(PackageSystem):
    def __init__(self, conn):
        super(CryptedPackageSystem, self).__init__(conn)

    def send_c(self, o, key):
        _, data = PackageEncoder(o).get_encoded()
        # print(data, key)
        data = Network(chatText).encrypt(data, key)
        length = len(data)

        len_str = str(length)

        for _ in range(32, len(len_str), -1):
            len_str = "0" + len_str

        # print(len(len_str))
        # print(len_str)

        self.conn.send(len_str.encode())
        self.conn.send(data)

    def recv_c(self, key):
        try:
            length = self.conn.recv(32)
            data = self.conn.recv(int(length.decode()))
        except ValueError:
            return None
        return PackageDecoder(Network(chatText).decrypt(data, key)).get_decoded()


class CustomScrollbar(Canvas):
    def __init__(self, parent, **kwargs):
        self.command = kwargs.pop("command", None)

        kw = kwargs.copy()
        if "fg" in kw.keys():
            del kw["fg"]
        Canvas.__init__(self, parent, **kw)
        if "fg" not in kwargs.keys():
            kwargs["fg"] = "darkgray"

        # coordinates are irrelevant; they will be recomputed
        # in the 'set' method\
        self._x0 = 0
        self._y0 = 0
        self._x1 = 0
        self._y1 = 0

        self.pressed_y = 0

        self.old_y = 0
        self.__id = self.create_rectangle(0, 0, 1, 1, fill=kwargs["fg"], outline=kwargs["fg"], tags=("thumb",))
        self.bind("<ButtonPress-1>", self.on_press)
        self.bind("<ButtonRelease-1>", self.on_release)

    def configure(self, cnf=None, **kw):
        self.command = kw.pop("command", None)
        # super().configure(cnf, **kw)

        fg = kw.pop("fg", "darkgray")

        super().configure(cnf, **kw)
        self.itemconfig(self.__id, fill=fg, outline=fg)

    def config(self, cnf=None, **kw):
        self.configure(cnf, **kw)

    # noinspection PyUnusedLocal
    def redraw(self, event):
        # The command is presumably the `yview` method of a widget.
        # When called without any arguments it will return fractions
        # which we can pass to the `set` command.
        self.set(*self.command())

    def set(self, first, last):
        first = float(first)
        last = float(last)
        height = self.winfo_height()
        x0 = 2
        x1 = self.winfo_width() - 2
        y0 = max(int(height * first), 0)
        y1 = min(int(height * last), height)
        self._x0 = x0
        self._x1 = x1
        self._y0 = y0
        self._y1 = y1

        self.coords("thumb", x0, y0, x1, y1)

    def on_press(self, event):
        self.bind("<Motion>", self.on_click)
        self.pressed_y = event.y
        self.on_click(event)

    # noinspection PyUnusedLocal
    def on_release(self, event):
        self.unbind("<Motion>")

    def on_click(self, event):
        y = event.y / self.winfo_height()
        y0 = self._y0
        y1 = self._y1
        # print(y0, y1)
        # print(y1-y0)
        # print((y1-y0)/2)
        a = y + ((y1 - y0) / -(self.winfo_height() * 2))
        # print(((y1-y0)/2)*y/100)
        self.command("moveto", a)


class OptionsWindow(Toplevel):
    def __init__(self, master: Frame, title):
        super().__init__(master)
        self.title(title)
        self.minsize(50, 5)
        self.bind("<Return>", lambda event: self.go())

        self.grab_set()
        self.focus_set()

    def go(self):
        pass

    def option_delete(self):
        """
        Deletes an option

        :return:
        """

        app.connecter.config(state=NORMAL)
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
            window.minsize(300, 100)
            window.maxsize(300, 100)
            Label(window, text=texty).pack()
            go = Button(window, text="OK", command=window.destroy)
            go.pack(side=BOTTOM)
            go.focus_set()


class Network(object):
    conn_array: List = []  # stores open sockets
    username_array: Dict = {}  # key: the open sockets in Network.conn_array, value: usernames for the connection
    secret_array: Dict = {}  # key: the open sockets in Network.conn_array, value: integers for encryption
    conn_init = None
    pak_array: Dict = {}

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
    def encrypt(b, key):
        from Crypto.Cipher import ARC4

        obj = ARC4.new(key.encode())
        return obj.encrypt(b)

    @staticmethod
    def decrypt(b, key):
        from Crypto.Cipher import ARC4

        obj2 = ARC4.new(key.encode())
        return obj2.decrypt(b)

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

    def net_send(self, conn, secret, o):
        """Sends message through the open socket conn with the encryption key
        secret. Sends the length of the incoming message, then sends the actual
        message.
    
        """
        try:
            print(f"SEND_DATA {conn.getpeername()[0]}:{conn.getpeername()[1]}: {o}")
            self.pak_array[conn].send_c(o, secret)
        except socket.error:
            if len(Network.conn_array) != 0:
                self.chatText.write_error(
                    "Sending message failed", "server")
                self.process_event(EVT_DISCONNECT)

    # noinspection PyUnusedLocal
    def net_catch(self, conn, secret):
        """Receive and return the message through open socket conn, decrypting
        using key secret. If the message length begins with - instead of a number,
        process as a flag and return 1.
    
        """
        try:
            data = self.pak_array[conn].recv_c(self.secret_array[conn])
            if data is None:
                return None
            print(f"RECV_DATA {conn.getpeername()[0]}:{conn.getpeername()[1]}: {data}")
            if "event" in data.keys():
                self.process_event(data["event"], conn, *data["args"], **data["kwargs"])
                return None
            if len(Network.conn_array) > 1:
                for connection in Network.conn_array:
                    if connection != conn:
                        self.net_send(connection, Network.secret_array[connection], data)
            return data
        except socket.error:
            if len(Network.conn_array) != 0:
                self.chatText.write_error(
                    "Retrieving of a message failed", "server")
            self.process_event(EVT_DISCONNECT)

    @staticmethod
    def is_prime(number):
        """Checks to see if a number is prime."""
        x = 1
        if number == 2 or number == 3:
            return True
        while x < math.sqrt(number):
            x += 1
            if number % x == 0:
                return False
        return True

    def send_event_all(self, event, *args, **kwargs):
        for connection in Network.conn_array:
            self.net_send(
                connection, Network.secret_array[connection], {"event": event, "args": args, "kwargs": kwargs}
            )
        # self.process_event(event, conn)

    def send_event(self, event, conn, *args, **kwargs):
        self.net_send(conn, Network.secret_array[conn], {"event": event, "args": args, "kwargs": kwargs})

    # noinspection PyUnusedLocal
    def process_event(self, event, conn=None, *args, **kwargs):
        """
        Process the flag corresponding to number, using open socket conn
        if necessary.

        :param event:
        :param conn:
        :return:
        """
        if event == EVT_DISCONNECT:  # disconnect
            # in the event of single connection being left or if we're just a client
            if len(Network.conn_array) == 1:
                message_window(app.main_frame, "Connection Lost", "Info")
                dump = Network.conn_array.pop()
                try:
                    dump.close()
                except socket.error:
                    message_window("Connection lost because of bad connection", "Warning")
                if not isCLI:
                    app.stateConnect.set("Lanceer")
                    app.connecter.config(state=NORMAL)
                return

            if conn is not None:
                self.chatText.write_warn(f"Connection with {conn.getsockname()[0]} lost", "Client")
                Network.conn_array.remove(conn)
                conn.close()
        if event == EVT_USERNAME_CHANGE:  # user_name change
            # name = self.net_catch(conn, Network.secret_array[conn])
            name = args[0]
            if self.is_username_free(name):
                self.chatText.write_info(
                    f"User {Network.username_array[conn]} has changed his/her name to: {name}", "server"
                )
                Network.username_array[conn] = name
                ContactsWindow.contact_array[conn.getpeername()[0]] = [conn.getpeername()[1], name]
        # passing a friend who this should connect to (I am assuming it will be
        # running on the same port as the other session)
        if event == EVT_CONTACT:
            pass
            # ip_ = args[0]
            # port_ = args[1]
            # Client(ip_, port_, chatText).start()

            # data = conn.recv(4)
            # data = conn.recv(int(data.decode()))
            # Client(data.decode(),
            #        int(ContactsWindow.contact_array[conn.getpeername()[0]][0]), chatText).start()

    def process_user_commands(self, command, param):
        """
        Processes commands passed in via the / text input.

        :param command:
        :param param:
        :return:
        """

        global user_name

        if command == "nick":  # change nickname
            for letter in param[0]:
                if letter == " " or letter == "\n":
                    if isCLI:
                        message_window(0, "Name can't contain spaces!")  # FIXME: Let useername can contian spaces
                    else:
                        message_window(app.main_frame, "Name can't contain spaces!")
                    return
            if self.is_username_free(param[0]):
                chatText.write_succes("Name is changed to: '" + param[0] + "'", "server")
                self.send_event_all(EVT_USERNAME_CHANGE, param[0])  # conn.send("-002".encode())
                # self.net_send(conn, Network.secret_array[conn], param[0])
                user_name = param[0]
            else:
                if isCLI:
                    message_window(0, param[0] + " is already used as name!")
                else:
                    message_window(app.main_frame, param[0] + " is already used as name!")
        if command == "disconnect":  # disconnects from current connection
            self.send_event_all(EVT_DISCONNECT)
            self.process_event(EVT_DISCONNECT)  # self.process_flag("-001")
        if command == "connect":  # connects to passed in host port
            if options_sanitation(param[1], param[0]):
                Client(param[0], int(param[1]), chatText).start()
        if command == "host":  # starts server on passed in port
            if options_sanitation(param[0]):
                Server(int(param[0]), chatText, Network(chatText)).start()
        if command == "help":
            chatText.write2screen(username="CONSOLE", text="Commands help:")
            chatText.write2screen(username="CONSOLE", text="  ::help")
            chatText.write2screen(username="CONSOLE", text="   - This help command")
            chatText.write2screen(username="CONSOLE", text="  ::nick <username>")
            chatText.write2screen(username="CONSOLE", text="   - Change username")
            chatText.write2screen(username="CONSOLE", text="  ::disconnect")
            chatText.write2screen(username="CONSOLE", text="   - Disconnects from a server")
            chatText.write2screen(username="CONSOLE", text="  ::connect <ip> <port>")
            chatText.write2screen(username="CONSOLE", text="   - Connects to a server")
            chatText.write2screen(username="CONSOLE", text="  ::host <port>")
            chatText.write2screen(username="CONSOLE", text="   - Hosts a server with the given port")
        if command == "colorrgb":
            global user_color
            error = False
            if not param[0].isdigit():
                chatText.write_error(username="CONSOLE", text="Red color is not a digit")
                error = True
            if not param[1].isdigit():
                chatText.write_error(username="CONSOLE", text="Green color is not a digit")
                error = True
            if not param[2].isdigit():
                chatText.write_error(username="CONSOLE", text="Blue color is not a digit")
                error = True
            if error:
                return
            red = int(param[0])
            green = int(param[1])
            blue = int(param[2])
            rhex = hex(red)[2:]
            ghex = hex(green)[2:]
            bhex = hex(blue)[2:]
            # print(len(bhex))
            if len(rhex) == 1:
                rhex = f"0{rhex}"
            if len(ghex) == 1:
                ghex = f"0{ghex}"
            if len(bhex) == 1:
                bhex = f"0{bhex}"
            user_color = f"#{rhex}{ghex}{bhex}"
            chatText.write_succes(username="CONSOLE", text=f"Color changed to '{user_color}'")

    @staticmethod
    def is_username_free(name):
        """
        Checks to see if the user_name name is free for use.

        :param name:
        :return:
        """

        for conn in Network.username_array:
            if name == Network.username_array[conn] or name == user_name:
                return False
        return True

    def pass_friends(self, conn):
        """
        Sends conn all of the people currently in Network.conn_array so they can connect to them.

        :param conn:
        :return:
        """

        for connection in Network.conn_array:
            if conn != connection:
                # conn.send("-004".encode())
                self.send_event(EVT_CONTACT, conn, connection.getpeername()[0], connection.getpeername()[1])

                # conn.send(
                #     self.format_number(len(connection.getpeername()[0])).encode())  # pass the ip address
                # conn.send(connection.getpeername()[0].encode())
                # conn.send(formatNumber(len(connection.getpeername()[1])).encode())  #pass the port number
                # conn.send(connection.getpeername()[1].encode())


class ClientOptions(OptionsWindow):
    def __init__(self, master: Frame):
        """
        Launches client options window for getting destination hostname
        and port.

        :param master:
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
    if isCLI:
        app.main_frame = 0
    if not por.isdigit():
        message_window(app.main_frame, "Enter port \"number\".")
        return False
    if int(por) < 0 or 65555 < int(por):
        message_window(app.main_frame, "A port number is a number between 0 and 65535")
        return False
    if loc != "":
        if not ip_process(loc.split(".")):
            message_window(app.main_frame, "Enter a correct ip please. Such as 127.0.0.1")
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
    def __init__(self, master: Frame):
        """
        Launches server options window for getting port.

        :param master:
        :return:
        """

        chat_text = chatText
        super().__init__(master, "Connection options")
        self.protocol("WM_DELETE_WINDOW", lambda: self.option_delete())

        frame_1 = Frame(self, bg=COLOR_WIN_BG)

        Label(frame_1, text="Port:", bg=COLOR_LBL_BG, fg=COLOR_LBL_FG).pack(side=LEFT)
        self.portNumber = Entry(
            frame_1, bg=COLOR_TEXT_INPUT_BG, fg=COLOR_TEXT_INPUT_FG, relief=RELIEF_TEXT_INPUT, border=BORDER_TEXT_INPUT
        )
        self.portNumber.pack(side=LEFT, fill=X, expand=True)
        self.portNumber.focus_set()

        frame_1.pack(fill=BOTH, expand=True)
        frame_2 = Frame(self, bg=COLOR_WIN_BG)

        go_btn = Button(
            frame_2, text="Launch", bg=COLOR_OK_BTN_BG, fg=COLOR_OK_BTN_FG, command=lambda: self.go(),
            relief=RELIEF_OK_BTN, border=BORDER_OK_BTN
        )
        go_btn.pack(side=RIGHT)

        frame_2.pack(fill=X, expand=True)

        self.chatText = chat_text

    def go(self):
        """
        Processes the options entered by the user in the
        server options window.

        :return:
        """
        p = self.portNumber.get()
        if options_sanitation(p):
            if not isCLI:
                self.destroy()
            Server(int(p), self.chatText, Network(chatText)).start()
        elif isCLI:
            sys.exit(1)


# -------------------------------------------------------------------------

class UsernameOptions(OptionsWindow):
    def __init__(self, master: Frame, network: Network):
        """
        Launches user_name options window for setting user_name.

        :param master:
        :return:
        """
        super().__init__(master, "User options")

        go_btn = Button(
            self, text="Change", command=lambda: self.go(), bg=COLOR_OK_BTN_BG, fg=COLOR_OK_BTN_FG,
            relief=RELIEF_OK_BTN, border=RELIEF_OK_BTN
        )
        go_btn.pack(side=BOTTOM)

        Label(
            self, text="Name:", bg=COLOR_LBL_BG, fg=COLOR_LBL_FG, relief=RELIEF_LBL, border=BORDER_LBL
        ).pack(side=LEFT)
        self.userName = Entry(
            self, bg=COLOR_TEXT_INPUT_BG, fg=COLOR_TEXT_INPUT_FG, relief=RELIEF_TEXT_INPUT, border=BORDER_TEXT_INPUT
        )
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

    :param title:
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
        window.minsize(300, 100)
        window.maxsize(300, 100)

        Label(window, text=texty).pack()
        go = Button(
            window, text="OK", command=window.destroy, bg=COLOR_OK_BTN_BG, fg=COLOR_OK_BTN_FG,
            relief=RELIEF_OK_BTN, border=BORDER_OK_BTN
        )
        go.pack(side=BOTTOM)
        go.focus_set()


class MessageWindow(object):
    def __init__(self, master: Optional[Union[Frame, Toplevel]] = None, texty: str = "", title: str = "Error"):
        if master:
            self.window = Toplevel(master)
        else:
            self.window = Tk()

        self.window.title(title)
        self.window.grab_set()
        self.window.minsize(300, 240)

        Label(self.window, text=texty, bg=COLOR_LBL_BG, fg=COLOR_LBL_FG, relief=RELIEF_LBL, border=BORDER_LBL).pack(TOP)
        ok_button = Button(
            self.window, text="OK", command=self.window.destroy, bg=COLOR_OK_BTN_BG, fg=COLOR_OK_BTN_FG,
            relief=RELIEF_OK_BTN, border=BORDER_OK_BTN
        )
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
    app.connecter.config(state=NORMAL)
    window.destroy()


# def send_text(text: str, network: Network = None):
#     """
#     Sends text to the clients
#
#     :param network:
#     :param text:
#     :return:
#     """
#
#     if not network:
#         network = Network(chatText)
#
#     for person in Network.conn_array:
#         network.net_send(person, Network.secret_array[person], text, None, "white")


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

        window = OptionsWindow(app.main_frame, "Verbindings opties")

        frame = Frame(window, bg=COLOR_WIN_BG)

        Label(frame, text="Server IP:", bg=COLOR_LBL_BG, fg=COLOR_LBL_FG).grid(row=0)
        destination = Entry(frame, bg=COLOR_TEXT_INPUT_BG, fg=COLOR_TEXT_INPUT_FG, relief=RELIEF_TEXT_INPUT,
                            border=BORDER_TEXT_INPUT)
        destination.grid(row=0, column=1)

        frame.go = lambda: client_connect(destination.get(), "9999")
        go = Button(frame, text="Verbind", command=lambda: (frame.go(), frame.destroy()),
                    bg=COLOR_OK_BTN_BG, fg=COLOR_OK_BTN_FG, activebackground=COLOR_OK_BTN_ACT,
                    relief=RELIEF_BTN, border=BORDER_BTN)
        go.grid(row=1, column=1)
        frame.pack(fill=BOTH, expand=True)

    @staticmethod
    def quick_server():
        """
        Quick-starts a server.
    
        :return:
        """

        server = Server(9999, chatText, Network(chatText))
        server.start()
        return server


class PasswordWindow(OptionsWindow):
    def __init__(self, master):
        """
        Menu window for connection options.

        :return:
        """

        super(PasswordWindow, self).__init__(master, "Change Password")

        frame = Frame(self, bg=COLOR_WIN_BG)

        Label(frame, text="Password:").grid(row=0)
        self.passwordEntry = Entry(frame, show="#", bg=COLOR_TEXT_INPUT_BG, fg=COLOR_TEXT_INPUT_FG,
                                   relief=RELIEF_TEXT_INPUT, border=BORDER_TEXT_INPUT)
        self.passwordEntry.grid(row=0, column=1)

        go = Button(frame, text="OK", command=self.go, bg=COLOR_BTN_BG, fg=COLOR_BTN_FG,
                    relief=RELIEF_BTN, border=BORDER_BTN)
        go.grid(row=1, column=1)
        frame.pack(fill=BOTH, expand=True)

    def go(self):
        global password
        password = self.passwordEntry.get()
        self.destroy()


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
            MessageWindow(app.main_frame, f"Can't save history\nIOErrror: {e.__str__()}")
            return
        MessageWindow(app.main_frame, "Can't save history")
    except Exception as e:
        MessageWindow(app.main_frame, f"Internal error when saving history\n{e.__class__.__name__}: {e.__str__()}")


class ClientType(object):
    clientType = 0

    @staticmethod
    def connects(client_type, network: Network):
        """
        Choose what client type, to choose the options of.
    
        :param network:
        :param client_type:
        :return:
        """

        app.connecter.config(state=DISABLED)
        if len(Network.conn_array) == 0:
            if client_type == 0:
                ClientOptions(app.main_frame)
            if client_type == 1:
                ServerOptions(app.main_frame)
        else:
            app.connecter.config(state=NORMAL)
            network.send_event_all(EVT_DISCONNECT)
            network.process_event(EVT_DISCONNECT)

    @staticmethod
    def disconnect(network=None):
        if network is None:
            network = Network(chatText)

        app.connecter.config(state=NORMAL)
        network.send_event_all(EVT_DISCONNECT)
        network.process_event(EVT_DISCONNECT)

    @staticmethod
    def to_client():
        """
        Client chat
    
        :return:
        """

        ClientType.clientType = 0

    @staticmethod
    def to_server():
        """
        Server chat
    
        :return:
        """

        ClientType.clientType = 1


class ContactsWindow(Toplevel):
    contact_array = {}

    def __init__(self, master: Frame):
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
        scrollbar = CustomScrollbar(self, relief=FLAT, border=0, width=10, highlightthickness=0,
                                    bg=COLOR_SCROLL_BG, fg=COLOR_SCROLL_FG, height=0)
        self.listbox = Listbox(self, yscrollcommand=scrollbar.set, border=0, relief=FLAT,
                               bg=COLOR_LIST_BG, fg=COLOR_LIST_FG, selectbackground=COLOR_LIST_SEL)
        scrollbar.config(command=self.listbox.yview)
        scrollbar.pack(side=RIGHT, fill=Y)
        buttons = Frame(self)
        c_but = Button(buttons, text="Connect", bg=COLOR_BTN_BG, fg=COLOR_BTN_FG, relief=FLAT, border=0,
                       command=lambda: self.contacts_connect())
        c_but.pack(side=LEFT)
        d_but = Button(buttons, text="Delete", bg=COLOR_BTN_BG, fg=COLOR_BTN_FG, relief=FLAT, border=0,
                       command=lambda: self.contacts_remove(
                       ))
        d_but.pack(side=LEFT)
        a_but = Button(buttons, text="Add", bg=COLOR_BTN_BG, fg=COLOR_BTN_FG, relief=FLAT, border=0,
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
        a_frame = Frame(a_window, bg=COLOR_WIN_BG)
        Label(a_frame, text="Name:", bg=COLOR_WIN_BG, fg=COLOR_WIN_FG).grid(row=0)
        name = Entry(a_frame, relief=FLAT, border=0, bg=COLOR_TEXT_INPUT_BG, fg=COLOR_TEXT_INPUT_FG)
        name.focus_set()
        name.grid(row=0, column=1)
        Label(a_frame, text="IP:", bg=COLOR_WIN_BG, fg=COLOR_WIN_FG).grid(row=1)
        ip = Entry(a_frame, relief=FLAT, border=0, bg=COLOR_TEXT_INPUT_BG, fg=COLOR_TEXT_INPUT_FG)
        ip.grid(row=1, column=1)
        Label(a_frame, text="Port:", bg=COLOR_WIN_BG, fg=COLOR_WIN_FG).grid(row=2)
        port_ = Entry(a_frame)
        port_.grid(row=2, column=1)
        go = Button(a_frame, text="Add", relief=FLAT, border=0, bg=COLOR_OK_BTN_BG, fg=COLOR_OK_BTN_FG,
                    command=lambda: self.contacts_add_helper(name.get(), ip.get(), port_.get(), a_window)
                    )
        go.grid(row=3, column=1)
        a_frame.pack(fill=BOTH, expand=TRUE)

    def contacts_add_helper(self, username: str, ip: str, port_: str, window: Toplevel):
        """
        Contact adding helper function. Recognizes invalid username's and
        adds contact to listbox and contact_array.
    
        :param username:
        :param ip:
        :param port_:
        :param window:
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
    global password

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
    if "password" in data["User"].keys():
        password = data["User"]["password"]
    else:
        password = None


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
            "name": user_name,
            "password": password
        }
    }
    file.save()
    file.close()


def send_message(msg_color, msg_text, msg_type, username):
    network = Network(chatText)

    for person in Network.conn_array:
        network.net_send(
            person, Network.secret_array[person], {
                "message": msg_text, "username": username, "color": msg_color, "type": msg_type
            }
        )


class ChatText(object):
    def __init__(self):
        self.rowNumber = 0
        self.colorNumber = 2

    def write2server(self, send=True, msg_color=None, msg_text="", msg_type="chat", username=None):
        """
        Places the text from the text bar on to the screen and sends it to
        everyone this program is connected to.

        :param username:
        :param msg_type:
        :param msg_text:
        :param msg_color:
        :param send:
        :return:
        """

        print(colorsys.rgb_to_hsv(eval("0x" + msg_color[1:3]) / 255,
                                  eval("0x" + msg_color[3:5]) / 255,
                                  eval("0x" + msg_color[5:7]) / 255)[2])

        if 1:
            if msg_type == "error":
                self.write_error(msg_text, username)
            elif msg_type == "warn":
                self.write_warn(msg_text, username)
            elif msg_type == "info":
                self.write_info(msg_text, username)
            elif msg_type == "success":
                self.write_succes(msg_text, username)
            else:
                if colorsys.rgb_to_hsv(eval("0x" + msg_color[1:3]) / 255,
                                       eval("0x" + msg_color[3:5]) / 255,
                                       eval("0x" + msg_color[5:7]) / 255)[2] >= 0.25:
                    self.write2screen(msg_color, "black", msg_text, user_name)
                else:
                    self.write2screen(msg_color, COLOR_TEXT_INPUT_BG, msg_text, user_name)
        if send:
            send_message(msg_color, msg_text, msg_type, username)

    def write2screen(self, fg='black', bg="white", text="", username=""):
        """
        Places text to main text body in format "[user_name]: text".
        The "color" is for the background

        :param fg:
        :param bg:
        :param text:
        :param username:
        :return:
        """

        global max_len
        global app
        if not isCLI:
            app.main_body.mainBodyText.config(state=NORMAL)
            text_b = text

            app.main_body.mainBodyText.insert(END, "[" + username + "]: ")
            app.main_body.mainBodyText.insert(END, text_b + "\n")

            self.rowNumber += 1
            app.main_body.mainBodyText.tag_add("color" + str(self.colorNumber), str(self.rowNumber) + ".0",
                                               str(self.rowNumber + 1) + ".0")
            app.main_body.mainBodyText.tag_config("color" + str(self.colorNumber), foreground=fg, background=bg,
                                                  font=("Courier New", 11))
            self.colorNumber += 1

            app.main_body.mainBodyText.yview(END)
            app.main_body.mainBodyText.config(state=DISABLED)
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
        self.write2screen('white', '#ff3737', text, username)

    def write_warn(self, text='', username=''):
        """
        Write a warning to the screen the "orange" color"

        :param text:
        :param username:
        :return:
        """
        self.write2screen('white', '#ffff37', text, username)

    def write_info(self, text: str = '', username: str = ''):
        """
        Write a info to the screen the "cyan" color

        :param text:
        :param username:
        :return:
        """
        self.write2screen('white', '#37a7a7', text, username)

    def write_succes(self, text: str = '', username: str = ''):
        """Write a succes to the screen the "green" color"""
        self.write2screen('white', '#37ff37', text, username)

    def write_chat(self, text: str = '', username: str = ''):
        """Write a succes to the screen the "darkcyan" color"""
        self.write2screen('black', 'white', text, username)


# places the text from the text bar on to the screen and sends it to
# everyone this program is connected to


#############################

#############################


# noinspection PyUnusedLocal
def process_user_text(event: Event, network: Network):
    """Takes text from text bar input and calls processUserCommands if it
    begins with '/'.

    """
    import shlex

    data = app.text_input.get()
    if data[0:2] != "::":  # is not a command
        chatText.write2server(True, user_color, data, username=user_name)
    else:
        # if data.find(" ") == -1:
        #     command = data[1:]
        # else:
        #     command = data[1:data.find(" ")]
        cmd_and_params = shlex.split(data[2:])
        params = cmd_and_params[1:]
        command = cmd_and_params[0]
        # params = data[data.find(" ") + 1:].split(" ")
        network.process_user_commands(command, params)
    app.text_input.delete(0, END)


def process_user_input(text: str, network: Network):
    """ClI version of processUserText."""
    if text[0] != "/":
        chatText.write2server(True, '#' + user_color, text, username=user_name)
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

    update_theme()

    # Set theme colors
    app.main_frame.config(bg=COLOR_WIN_BG)
    app.main_body_text.config(bg=COLOR_CHAT_BG)
    app.body_text_scroll.config(bg=COLOR_SCROLL_BG, fg=COLOR_SCROLL_FG)
    app.client_type_1.config(bg=COLOR_CLIENT_TYPE_BG, fg=COLOR_CLIENT_TYPE_FG, selectcolor=COLOR_CLIENT_TYPE_ACT)
    app.client_type_2.config(bg=COLOR_CLIENT_TYPE_BG, fg=COLOR_CLIENT_TYPE_FG, selectcolor=COLOR_CLIENT_TYPE_ACT)
    app.connecter.config(bg=COLOR_CONNECTER_BG, fg=COLOR_CONNECTER_FG, activebackground=COLOR_ACCENT)


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
            # print("RECV DATA:", data)

            if data is None:
                continue
            if "event" in data.keys():
                continue
            if "message" not in data.keys():
                continue
            if "username" not in data.keys():
                continue
            if "color" not in data.keys():
                continue
            if "type" not in data.keys():
                continue

            msg_type = data["type"]
            msg_text = data["message"]
            msg_color = data["color"]
            username = data["username"]

            if msg_type == "error":
                self.chatText.write_error(msg_text, username)
            elif msg_type == "warn":
                self.chatText.write_warn(msg_text, username)
            elif msg_type == "info":
                self.chatText.write_info(msg_text, username)
            elif msg_type == "success":
                self.chatText.write_succes(msg_text, username)
            else:
                if colorsys.rgb_to_hsv(eval("0x" + msg_color[1:3]) / 255,
                                       eval("0x" + msg_color[3:5]) / 255,
                                       eval("0x" + msg_color[5:7]) / 255)[2] >= 0.25:
                    self.chatText.write2screen(msg_color, 'black', msg_text, username)
                else:
                    self.chatText.write2screen(msg_color, COLOR_TEXT_INPUT_BG, msg_text, username)
            # if send:
            #     send_message(msg_color, msg_text, msg_type, username)
            #
            # if data != 1:
            #     if data["type"] != -1:
            #         self.chatText.write2screen('white', "red",
            #                                    data[data.find(" text=") + 6:],
            #                                    data[data.find(';') + 1 + 7 + len("user_name="):data.find(' text=')])
            #     elif data.find("*Warn") != -1:
            #         self.chatText.write2screen('white', "orange",
            #                                    data[data.find(" text=") + 6:],
            #                                    data[data.find(';') + 1 + 6 + len("user_name="):data.find(' text=')])
            #     elif data.find("*Info") != -1:
            #         self.chatText.write2screen('white', "blue",
            #                                    data[data.find(" text=") + 6:],
            #                                    data[data.find(';') + 1 + 6 + len("user_name="):data.find(' text=')])
            #     elif data.find("*Succes") != -1:
            #         self.chatText.write2screen('white', "green",
            #                                    data[data.find(" text=") + 6:],
            #                                    data[data.find(';') + 1 + 8 + len("user_name="):data.find(' text=')])
            #     else:
            #         user_color2 = data[data.find('#') + 1:data.find(';')].lower()
            #         if colorsys.rgb_to_hsv(eval("0x" + user_color[0:2]) / 255,
            #                                eval("0x" + user_color[2:4]) / 255,
            #                                eval("0x" + user_color[4:6]) / 255)[2] >= 0.5:
            #             self.chatText.write2screen('black', user_color2, data[data.find(';') + 1:],
            #                                        Network.username_array[conn])
            #         else:
            #             self.chatText.write2screen('white', user_color2, data[data.find(';') + 1:],
            #                                        Network.username_array[conn])


# -------------------------------------------------------------------------
class Server(ChatThread):
    "A class for a Server instance."""

    def __init__(self, port_, chat_text: ChatText, network: Network):
        super(Server, self).__init__(chat_text, network)
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

            conn_init, addr_init = s.accept()
            pak_init = PackageSystem(conn_init)
            serv = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            serv.bind(('', 0))  # get a random empty port_
            serv.listen(1)

            port_val = serv.getsockname()[1]
            # if len(port_val) == 5:
            #     conn_init.send(port_val.encode())
            # else:
            #     conn_init.send(("0" + port_val).encode())

            pak_init.send({"port": port_val})

            conn_init.close()
            conn, addr = serv.accept()
            pak = PackageSystem(conn)
            Network.conn_array.append(conn)  # add an array entry for this connection
            Network.pak_array[conn] = CryptedPackageSystem(conn)
            self.chatText.write_succes("Connected with server " + str(addr[0]))

            if not isCLI:
                app.stateConnect.set("Verbinding verbreken")
                app.connecter.config(state=NORMAL)

            # create the numbers for my encryption
            # prime = randint(1000, 9000)
            # while not self.network.is_prime(prime):
            #     prime = randint(1000, 9000)
            # base = randint(20, 100)
            # a = randint(20, 100)

            # # send the numbers (base, prime, A)
            # conn.send(self.network.format_number(len(str(base))).encode())
            # conn.send(str(base).encode())
            #
            # conn.send(self.network.format_number(len(str(prime))).encode())
            # conn.send(str(prime).encode())
            #
            # conn.send(self.network.format_number(len(str(pow(base, a) % prime))).encode())
            # conn.send(str(pow(base, a) % prime).encode())

            pak.send({"secret": password})

            # # get B
            # data = conn.recv(4)
            # data = conn.recv(int(data.decode()))
            # b = int(data.decode())
            joined_phase2 = pak.recv()
            secret = joined_phase2["secret"]
            data = joined_phase2["username"]

            # calculate the encryption key
            # secret = pow(b, a) % prime
            # store the encryption key by the connection
            Network.secret_array[conn] = secret

            # conn.send(self.network.format_number(len(user_name)).encode())
            # conn.send(user_name.encode())

            pak.send({"username": user_name})

            # data = conn.recv(4)
            # data = conn.recv(int(data.decode()))
            if data is not None:
                Network.username_array[conn] = data
                contact_array[str(addr[0])] = [str(self.port), data]
            else:
                Network.username_array[conn] = addr[0]
                contact_array[str(addr[0])] = [str(self.port), f"{str(addr[0])}"]

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
        super(Client, self).__init__(chat_text, Network(chat_text))
        self.port = port_
        self.host = host

    def run(self):
        """

        :return:
        """
        conn_init2 = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        conn_init2.settimeout(5.0)
        pak_init = PackageSystem(conn_init2)
        try:
            conn_init2.connect((self.host, self.port))
        except socket.timeout:
            self.chatText.write_error("Timeout-melding. Host is mogelijk niet hier.", "client")
            app.connecter.config(state=NORMAL)
            raise SystemExit(0)
        except socket.error:
            self.chatText.write_error("Connectie melding. Host heeft net de verbinding geweigerd.", "server")
            app.connecter.config(state=NORMAL)
            raise SystemExit(0)

        # Get server port
        server_port_data = pak_init.recv()
        server_port = server_port_data["port"]

        # Close connection initializer
        del pak_init
        conn_init2.close()

        # Chat connector
        conn = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        conn.connect((self.host, server_port))
        pak = PackageSystem(conn)

        # Write status
        self.chatText.write_succes("Verbonden met: " + self.host +
                                   " op poort: " + str(server_port), "server")

        # Set connection state
        app.stateConnect.set("Verbinding verbreken")
        app.connecter.config(state=NORMAL)

        Network.conn_array.append(conn)
        Network.pak_array[conn] = CryptedPackageSystem(conn)

        socket.gethostbyname(socket.gethostname())

        pre_secret = pak.recv()
        secret = pre_secret["secret"]

        # print("client:", secret)

        # from urllib.request import urlopen
        # my_ip = urlopen('http://ip.42.pl/raw').read()

        # b = randint(20, 100)
        pak.send({"username": user_name, "secret": password})

        # secret = pow(a, b) % prime
        Network.secret_array[conn] = secret

        temp0001 = pak.recv()
        username_server = temp0001["username"]
        if username_server is not None:
            Network.username_array[conn] = username_server
            contact_array[conn.getpeername()[0]] = [str(self.port), username_server]
        else:
            Network.username_array[conn] = self.host
            contact_array[conn.getpeername()[0]] = [str(self.port), f"{conn.getpeername()[0]}"]
        threading.Thread(target=self.runner, args=(conn, secret)).start()


class MainMenuBar(Menu):
    def __init__(self, frame, app_):
        super().__init__(frame)

        # File menu
        file_menu = Menu(self, tearoff=0)
        file_menu.add_command(label="Save chat", command=lambda: save_history(app_.main_body.mainBodyText))
        file_menu.add_command(label="Change username",
                              command=lambda: UsernameOptions(frame, Network(chatText)))
        file_menu.add_command(label="Change password",
                              command=lambda: PasswordWindow(frame))
        file_menu.add_command(label="Change color", command=lambda: set_color())
        file_menu.add_command(label="Exit", command=lambda: frame.destroy())
        self.add_cascade(label="File", menu=file_menu)

        # Connection menu
        connection_menu = Menu(self, tearoff=0)
        connection_menu.add_command(label="Quick connect", command=QuickNetwork.quick_client)
        connection_menu.add_command(
            label="Connect with port", command=lambda: ClientOptions(frame))
        connection_menu.add_command(
            label="Disconnect", command=lambda: Network(chatText).process_event(EVT_DISCONNECT))
        self.add_cascade(label="Connect", menu=connection_menu)
        # Server menu
        server_menu = Menu(self, tearoff=0)
        server_menu.add_command(label="Launch server", command=QuickNetwork.quick_server)
        server_menu.add_command(label="Launch server with port",
                                command=lambda: ServerOptions(frame))
        self.add_cascade(label="Server", menu=server_menu)

        # Contacts entry
        self.add_command(label="Contacts", command=lambda: ContactsWindow(frame))


class MainBody(Frame):
    def __init__(self, frame):
        super().__init__(frame, relief=FLAT, border=0)

        # Create text and scrollbar
        self.mainBodyText = Text(self, relief=FLAT, border=0, bg=COLOR_TEXT_INPUT_BG)
        self.bodyTextScroll = CustomScrollbar(
            self, fg=COLOR_SCROLL_FG, bg=COLOR_SCROLL_BG, width=10, highlightthickness=0
        )

        # Packing text and scrollbar
        self.bodyTextScroll.pack(side=RIGHT, fill=Y)
        self.mainBodyText.pack(side=LEFT, fill=BOTH, expand=True)

        # Configurate text and scrollbar
        self.bodyTextScroll.config(command=self.mainBodyText.yview)
        self.mainBodyText.config(yscrollcommand=self.bodyTextScroll.set)

        # Pack MainBody
        self.pack(fill=BOTH, expand=True)

        # Disables the chat text (frame)
        self.mainBodyText.config(state=DISABLED)


class MainChatInput(Entry):
    def __init__(self, frame):
        super(MainChatInput, self).__init__(frame, relief=FLAT, border=0, bg=COLOR_TEXT_INPUT_BG)
        self.bind("<Return>", lambda evt: process_user_text(evt, Network(chatText)))
        self.pack(fill=X, padx=2, pady=2)
        self.focus_set()


class MainConnType(object):
    def __init__(self, main_frame):
        # Create state connection
        self.stateConnect = StringVar()
        self.stateConnect.set("Lanceer server")
        self.clientType = 1

        self.client_type_1 = Radiobutton(
            main_frame, text="Client", variable=self.clientType, selectcolor=COLOR_CLIENT_TYPE_ACT, value=0,
            command=ClientType.to_client, indicatoron=FALSE, relief=RELIEF_CLIENT_TYPE, border=BORDER_CLIENT_TYPE,
            bg=COLOR_CLIENT_TYPE_BG, fg=COLOR_CLIENT_TYPE_FG, width=10
        )
        self.client_type_2 = Radiobutton(
            main_frame, text="Server", variable=self.clientType, selectcolor=COLOR_CLIENT_TYPE_ACT, value=1,
            command=ClientType.to_server, indicatoron=FALSE, relief=RELIEF_CLIENT_TYPE, border=BORDER_CLIENT_TYPE,
            bg=COLOR_CLIENT_TYPE_BG, fg=COLOR_CLIENT_TYPE_FG, width=10
        )
        self.client_type_1.pack(anchor=E)
        self.client_type_2.pack(anchor=E)
        self.connecter = Button(
            main_frame, textvariable=self.stateConnect, relief=FLAT, bg=COLOR_CONNECTER_BG, fg=COLOR_CONNECTER_FG,
            command=lambda: ClientType.connects(self.clientType, Network(chatText)), activebackground=COLOR_ACCENT
        )
        self.connecter.pack()


class App(Tk):
    def __init__(self):
        super(App, self).__init__()

        self.title(titleText + " " + chatVersion)
        self.protocol("WM_DELETE_WINDOW", lambda: self.exit_app())

        # Load data and update theme
        load_data()
        update_theme()

        # Main frame, used for window background
        self.main_frame = Frame(self, relief=FLAT, border=0, highlightthickness=0, bg=COLOR_WIN_BG)
        self.main_frame.pack(fill=BOTH, expand=TRUE)

        # Create menu bar
        self.menubar = MainMenuBar(self.main_frame, self)

        # Sets menu bar
        self.config(menu=self.menubar)

        # Main body
        self.main_body = MainBody(self.main_frame)

        # Create chat input
        self.text_input = MainChatInput(self.main_frame)

        # Connection state radiobutton:
        self.connType = MainConnType(self.main_frame)

        if password is None:
            pass_window = PasswordWindow(self.main_frame)
            pass_window.mainloop()
            dump_data()

        # Welcome message
        if welcomeSign:
            chatText.write2screen('white', "black", f"{user_name}, welcome on the chat application", "")

        # ------------------------------------------------------------#

        # Main loop
        self.main_frame.mainloop()

        # Saving the data. (If changed of course)
        dump_data()

    @staticmethod
    def exit_app():
        dump_data()
        os.kill(os.getpid(), 0)


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "-cli":
        # CommandLine Interface (CLI) chat
        print("Starting Commandline Interface chat")
    else:
        chatText = ChatText()
        # Create window
        global app
        app = App()
