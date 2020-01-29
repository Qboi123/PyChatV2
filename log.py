import io
import os
import sys
from time import gmtime, strftime
from tkinter import Text
from typing import Iterable
import traceback


class Log(io.IOBase):
    def __init__(self, file, std, writeerror, name="Out", write_std=False):
        self.writeStd = write_std
        self.file = file
        self.std = std
        self.name = name
        self.old = "\n"
        self.fp = None
        self.writeError = writeerror
        if not os.path.exists("logs"):
            os.makedirs("logs")

    def write(self, o: str):
        l = o.splitlines(True)
        for i in l:
            if self.old[-1] == "\n":
                if self.writeStd:
                    self.std.write(strftime(f"%d-%m-%Y %H:%M:%S | {self.name} | ", gmtime()) + i)
                self.fp = open(self.file, "a+")
                self.fp.write(strftime(f"%d-%m-%Y %H:%M:%S | {self.name} | ", gmtime()) + i)
                self.fp.close()
            else:
                if self.writeStd:
                    self.std.write(i)
                self.fp = open(self.file, "a+")
                self.fp.write(i)
                self.fp.close()
            self.old = i

    def writelines(self, lines: Iterable[str]) -> None:
        for line in lines:
            self.write(line)

    def potato(self, exefile):
        self.write(exefile)
        self.flush()

    def flush(self):
        pass

    def fileno(self):
        self.fp = open(self.file, "a+")
        fileno = self.fp.fileno()
        self.fp.close()
        return fileno

    def read(self):
        import time
        if self.writeStd:
            self.std.write("[{time}] [In]: ".format(time=time.ctime(time.time())))

        a = self.std.read()
        self.fp = open(self.file, "a+")
        self.fp.write("[{time}] [In]: ".format(time=time.ctime(time.time())) + a)
        self.fp.close()
