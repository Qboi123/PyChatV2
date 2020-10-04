import pickle
import struct
import time
import urllib.request
from decimal import Decimal
from fractions import Fraction
from http.client import HTTPResponse
# noinspection PyProtectedMember
from io import RawIOBase, BytesIO
from math import ceil
from typing import Optional as _Optional, Any as _Any, List as _List, BinaryIO

import dill


class IntegerIO(BytesIO):
    def __init__(self, initial_value=0):
        super(IntegerIO, self).__init__()
        self.write(initial_value)

    # noinspection PyTypeChecker
    def read(self, size=None, index=0) -> int:
        if size is not None:
            raise ValueError("argument 'size' must be a NoneType object")
        if index < 0:
            raise ValueError("argument 'index' must be a non-negative integer")
        if not isinstance(index, int):
            raise TypeError("argument 'index' must be an integer")

        super(IntegerIO, self).seek(index * 1024)
        int.from_bytes(super(IntegerIO, self).read(1024), "little")

    def write(self, value: int, index=0) -> None:
        if index < 0:
            raise ValueError("argument 'index' must be a non-negative integer")
        if not isinstance(index, int):
            raise TypeError("argument 'index' must be an integer")

        super(IntegerIO, self).seek(index * 1024)
        super(IntegerIO, self).write(int.to_bytes(value, 1024, "little"))


class FloatIO(BytesIO):
    def __init__(self, initial_value=0):
        super(FloatIO, self).__init__()
        self.write(initial_value)

    # noinspection PyTypeChecker
    def read(self, size=None, index=0) -> int:
        if size is not None:
            raise ValueError("argument 'size' must be a NoneType object")
        if index < 0:
            raise ValueError("argument 'index' must be a non-negative integer")
        if not isinstance(index, int):
            raise TypeError("argument 'index' must be an integer")

        super(FloatIO, self).seek(index * 1024)
        size = int.from_bytes(super(FloatIO, self).read(4), "little")
        struct.unpack("f", super(FloatIO, self).read(size))

    def write(self, value: float, index=0) -> None:
        """
        Writes a float in the io stream at the given index.
        The offset is based on the index specified, calculated by ``{index} * 1024``.

        :param float value: The value to write to the stream.
        :param int index: The index to write the value to.
        :raises ValueError: If the index is a non-negative integer.
        :raises TypeError: If the index is not an integer.
        :raises OverflowError: If the float value is too large to fit in 1020 bytes.
        :return:
        """

        if index < 0:
            raise ValueError("argument 'index' must be a non-negative integer")
        if not isinstance(index, int):
            raise TypeError("argument 'index' must be an integer")

        data = struct.pack("f", value)
        if len(data) >= 1020:
            raise OverflowError("Float value too large to fit in 1020 bytes: {}".format(value))
        size = len(data)
        super(FloatIO, self).seek(index * 1024)
        super(FloatIO, self).write(int.to_bytes(size, 4, "little"))
        super(FloatIO, self).seek((index * 1024) + 4)
        super(FloatIO, self).write(data)


class BooleanIO(BytesIO):
    def __init__(self, initial_value=False):
        super(BooleanIO, self).__init__()
        self.write(initial_value)

    def read(self, size=None, id_=0) -> _Optional[bool]:
        if size is not None:
            raise ValueError("argument 'size' must be a NoneType object")
        super(BooleanIO, self).seek(id_)
        byte = super(BooleanIO, self).read()
        if byte == b"\1":
            return True
        elif byte == b"\0":
            return False
        else:
            return None

    def write(self, value: bool, id_=0) -> None:
        super(BooleanIO, self).seek(id_)
        super(BooleanIO, self).write(b"\0" if value is False else b"\1" if value is True else b"\f")


class NullIO(RawIOBase):
    def __init__(self):
        """
        Sends the data to a null stream. Literly writing nothing, and reading nothing.
        """

        super(NullIO, self).__init__()

    def read(self, size=None):
        return b""

    def write(self, data):
        return


class WebIO(BytesIO):
    def __init__(self, url, data=None, timeout=None, *, cafile=None, capath=None):
        super(WebIO, self).__init__()
        self.url = url
        self._fd: HTTPResponse = urllib.request.urlopen(url, data, timeout, cafile=cafile, capath=capath)

    def read(self, __size: _Optional[int] = ...) -> bytes:
        return self._fd.read(__size)

    def read1(self, __size: _Optional[int] = ...) -> bytes:
        return self._fd.read1(__size)

    def readable(self) -> bool:
        return self._fd.readable()

    def write(self, data):
        self._fd.write(data)

    def writable(self) -> bool:
        return self._fd.writable()

    def writelines(self, __lines: _Any) -> None:
        self._fd.writelines(__lines)

    def flush(self) -> None:
        self._fd.flush()

    def fileno(self) -> int:
        return self._fd.fileno()

    def readinto(self, __buffer) -> int:
        return self._fd.readinto(__buffer)

    def readinto1(self, __buffer) -> int:
        return self._fd.readinto1(__buffer)

    def readline(self, __size: _Optional[int] = ...) -> bytes:
        return self._fd.readline(__size)

    def readlines(self, __size: int = ...) -> _List[bytes]:
        return self._fd.readlines(__size)

    def seek(self, __pos: int, __whence: int = ...) -> int:
        return self._fd.seek(__pos, __whence)

    def tell(self) -> int:
        return self._fd.tell()

    def truncate(self, __size: _Optional[int] = ...) -> int:
        return self._fd.truncate(__size)

    def seekable(self) -> bool:
        return self._fd.seekable()


class DillIO(RawIOBase):
    def __init__(self):
        super(DillIO, self).__init__()

    def read(self, size=None):
        if size is not None:
            raise ValueError("argument 'size' must be a NoneType object")
        dill.loads(super(DillIO, self).read())

    def write(self, data):
        super(DillIO, self).write(dill.dumps(data))


class PickleIO(RawIOBase):
    def __init__(self):
        super(PickleIO, self).__init__()

    def read(self, size=None):
        if size is not None:
            raise ValueError("argument 'size' must be a NoneType object")
        pickle.loads(super(PickleIO, self).read())

    def write(self, data):
        super(PickleIO, self).write(pickle.dumps(data))


class DeviceIO(object):
    def __init__(self, *args, **kwargs):
        raise NotImplementedError("This will be may be implemented in the future.")


class ObjectIO(RawIOBase):
    def __init__(self, parent: BinaryIO):
        super(ObjectIO, self).__init__()

        self._parent = parent

    def read_int(self, *, unsigned=False, byteorder="little") -> int:
        ident = self.__read_identifier()
        if ident != 0x01:
            raise TypeError("Invalid identifier: " + hex(ident) + ", expected 0x01 for int type.")

        byte_len: bytes = self._parent.read(2)
        length: int = struct.unpack("h", byte_len)[0]

        data: bytes = self._parent.read(length)
        value: int = int.from_bytes(data, byteorder=byteorder, signed=(not unsigned))
        return value

    def write_int(self, value: int, *, unsigned=False, byteorder="little") -> None:
        from math import log

        def bytes_needed(n):
            if n == 0:
                return 1
            return int(ceil(log(n, 256))) + 1

        self.__write_identifier(0x01)

        length: int = bytes_needed(value)
        byte_len: bytes = struct.pack("H", length)
        self._parent.write(byte_len)

        data: bytes = int.to_bytes(value, length, byteorder, signed=(not unsigned))
        self._parent.write(data)

    def read_bool(self) -> bool:
        ident = self.__read_identifier()
        if ident != 0x02:
            raise TypeError("Invalid identifier: " + hex(ident) + ", expected 0x02 for bool type.")

        data: bytes = self._parent.read(1)
        number: int = int.from_bytes(data, "little")
        return number == 1

    def write_bool(self, value: bool) -> None:
        self.__write_identifier(0x02)

        number: int = 1 if value else 0
        data: bytes = int.to_bytes(number, 1, "little")
        self._parent.write(data)

    def read_str(self, *, encoding: str = "utf-8", errors: str = "strict") -> str:
        ident = self.__read_identifier()
        if ident != 0x03:
            raise TypeError("Invalid identifier: " + hex(ident) + ", expected 0x03 for str type.")

        byte_len: bytes = self._parent.read(8)
        length: int = struct.unpack("Q", byte_len)[0]

        data: bytes = self._parent.read(length)
        value: str = data.decode(encoding, errors)
        return value

    def write_str(self, value: str, *, encoding: str = "utf-8", errors: str = "strict"):
        self.__write_identifier(0x03)

        data: bytes = value.encode(encoding, errors)
        length: int = len(data)
        byte_len: bytes = struct.pack("Q", length)

        self._parent.write(byte_len)
        self._parent.write(data)

    def read_bytes(self) -> bytes:
        ident = self.__read_identifier()
        if ident != 0x04:
            raise TypeError("Invalid identifier: " + hex(ident) + ", expected 0x04 for bytes type.")

        byte_len: bytes = self._parent.read(8)
        length: int = struct.unpack("Q", byte_len)[0]

        data: bytes = self._parent.read(length)
        return data

    def write_bytes(self, value: bytes):
        self.__write_identifier(0x04)

        length: int = len(value)
        byte_len: bytes = struct.pack("Q", length)

        self._parent.write(byte_len)
        self._parent.write(value)

    def read_bytearray(self) -> bytearray:
        ident = self.__read_identifier()
        if ident != 0x06:
            raise TypeError("Invalid identifier: " + hex(ident) + ", expected 0x06 for bytearray type.")

        byte_len: bytes = self._parent.read(8)
        length: int = struct.unpack("Q", byte_len)[0]

        data: bytes = self._parent.read(length)
        return bytearray(data)

    def write_bytearray(self, value: bytearray):
        self.__write_identifier(0x06)

        length: int = len(value)
        byte_len: bytes = struct.pack("Q", length)

        self._parent.write(byte_len)
        self._parent.write(bytes(value))

    """
    /**
     * Saves the state of the {@code ArrayList} instance to a stream
     * (that is, serializes it).
     *
     * @param s the stream
     * @throws java.io.IOException if an I/O error occurs
     * @serialData The length of the array backing the {@code ArrayList}
     *             instance is emitted (int), followed by all of its elements
     *             (each an {@code Object}) in the proper order.
     */
    @java.io.Serial
    private void writeObject(java.io.ObjectOutputStream s)
        throws java.io.IOException {
        // Write out element count, and any hidden stuff
        int expectedModCount = modCount;
        s.defaultWriteObject();

        // Write out size as capacity for behavioral compatibility with clone()
        s.writeInt(size);

        // Write out all elements in the proper order.
        for (int i=0; i<size; i++) {
            s.writeObject(elementData[i]);
        }

        if (modCount != expectedModCount) {
            throw new ConcurrentModificationException();
        }
    }
"""

    def write_list(self, value: list):
        self.__write_identifier(0x10)
        self.write_int(len(value))

        for item in value:
            self.write_object(item)

    def read_list(self) -> list:
        ident = self.__read_identifier()
        if ident != 0x10:
            raise TypeError("Invalid identifier: " + hex(ident) + ", expected 0x10 for list type.")

        value: list = []
        length = self.read_int()

        for i in range(length):
            value.append(self.read_object())

        return value

    def write_tuple(self, value: tuple):
        self.__write_identifier(0x11)
        self.write_int(len(value))

        for item in value:
            self.write_object(item)

    def read_tuple(self) -> tuple:
        ident = self.__read_identifier()
        if ident != 0x11:
            raise TypeError("Invalid identifier: " + hex(ident) + ", expected 0x11 for tuple type.")

        value: list = []
        length = self.read_int()

        for i in range(length):
            value.append(self.read_object())

        return tuple(value)

    def write_set(self, value: set):
        self.__write_identifier(0x11)
        self.write_int(len(value))

        for item in value:
            self.write_object(item)

    def read_set(self) -> set:
        ident = self.__read_identifier()
        if ident != 0x11:
            raise TypeError("Invalid identifier: " + hex(ident) + ", expected 0x11 for tuple type.")

        value: list = []
        length = self.read_int()

        for i in range(length):
            value.append(self.read_object())

        return set(value)

    def write_dict(self, value: dict):
        self.__write_identifier(0x13)
        self.write_int(len(value))

        for key, val in value.items():
            self.write_object(key)
            self.write_object(val)

    def read_dict(self) -> dict:
        ident = self.__read_identifier()
        if ident != 0x13:
            raise TypeError("Invalid identifier: " + hex(ident) + ", expected 0x13 for dict type.")

        value: dict = {}
        length = self.read_int()

        for i in range(length):
            key = self.read_object()
            val = self.read_object()

            value[key] = val

        return value

    def write_float(self, value: float):
        self.__write_identifier(0x05)

        a, b = value.as_integer_ratio()
        self.write_int(a)
        self.write_int(b)

    def read_float(self):
        ident = self.__read_identifier()
        if ident != 0x05:
            raise TypeError("Invalid identifier: " + hex(ident) + ", expected 0x05 for float type.")

        a = self.read_int()
        b = self.read_int()

        c = float(a) / float(b)

        return c

    def __read_identifier(self):
        return int.from_bytes(self._parent.read(1), "little", signed=False)

    def __write_identifier(self, param):
        self._parent.write(int.to_bytes(param, 1, "little", signed=False))

    def write_object(self, item):
        if isinstance(item, bool):
            self.write_bool(item)
        elif isinstance(item, float):
            self.write_float(item)
        elif isinstance(item, int):
            self.write_int(item)
        elif isinstance(item, str):
            self.write_str(item)
        elif isinstance(item, bytes):
            self.write_bytes(item)
        elif isinstance(item, bytearray):
            self.write_bytearray(item)
        elif isinstance(item, tuple):  # tuple):
            self.write_tuple(item)
        elif isinstance(item, list):  # list
            self.write_list(item)
        elif isinstance(item, set):  # list
            self.write_set(item)
        elif isinstance(item, dict):
            self.write_dict(item)
        else:
            raise TypeError(f"Unknown object type: {type(item).__module__}.{type(item).__name__}")

    def read_object(self):
        ident = self.__read_identifier()
        self._parent.seek(self._parent.tell() - 1)

        if ident == 0x01:
            return self.read_int()
        elif ident == 0x02:
            return self.read_bool()
        elif ident == 0x03:
            return self.read_str()
        elif ident == 0x04:
            return self.read_bytes()
        elif ident == 0x05:
            return self.read_float()
        elif ident == 0x06:
            return self.read_bytearray()
        elif ident == 0x10:
            return self.read_list()
        elif ident == 0x11:
            return self.read_tuple()
        elif ident == 0x12:
            return self.read_set()
        elif ident == 0x13:
            return self.read_dict()
        else:
            raise TypeError("unknown identifier: " + hex(ident))


if __name__ == '__main__':
    def test1():
        a = 305
        bio = BytesIO()
        io: ObjectIO = ObjectIO(bio)
        io.write_int(a)

        data = bio.getvalue()

        bio = BytesIO(data)
        io: ObjectIO = ObjectIO(bio)
        print(repr(io.read_int()))


    def test2():
        a = 305.5
        bio = BytesIO()
        io: ObjectIO = ObjectIO(bio)
        io.write_float(a)

        data = bio.getvalue()

        bio = BytesIO(data)
        io: ObjectIO = ObjectIO(bio)
        print(repr(io.read_float()))


    def test3():
        a = "Hello World"
        bio = BytesIO()
        io: ObjectIO = ObjectIO(bio)
        io.write_str(a)

        data = bio.getvalue()

        bio = BytesIO(data)
        io: ObjectIO = ObjectIO(bio)
        print(repr(io.read_str()))


    def test4():
        a = b"\x00\x01\x02\x03\x04\x05\x06\x07\x08\t"
        bio = BytesIO()
        io: ObjectIO = ObjectIO(bio)
        io.write_bytes(a)

        data = bio.getvalue()

        bio = BytesIO(data)
        io: ObjectIO = ObjectIO(bio)
        print(repr(io.read_bytes()))


    def test5():
        a = True
        bio = BytesIO()
        io: ObjectIO = ObjectIO(bio)
        io.write_bool(a)

        data = bio.getvalue()

        bio = BytesIO(data)
        io: ObjectIO = ObjectIO(bio)
        print(repr(io.read_bool()))

    def test6():
        b = ["Hallo", 300, 504.35, True, b"Binary", ["Hello World", 57458943, 855493.47958365341, False, b"Binary version 2"], {"Key": "Value", "Number": 300}, bytearray(b"Hello World \x01\02\x03")]
        a = b * 1
        print(len(a))
        start = time.time()
        bio = BytesIO()
        io: ObjectIO = ObjectIO(bio)
        io.write_list(a)

        data = bio.getvalue()

        with open("test.qdat", "w+b") as file:
            file.write(data)
            file.flush()
            file.close()

        bio = BytesIO(data)
        io: ObjectIO = ObjectIO(bio)
        end = time.time()
        print(repr(io.read_list()))
        print("Time: " + str(end - start))

    def test7():
        a = {"Hallo", 300, 504.35, True, b"Binary", 545, 4654, 4653643, 54, 6, 4464, 66.466, 65664634.65634636, 46346.6, 634, 63464646356, 34, 6, 346, 4, 6, 5, 5, 1, 2, 3, 4, 5, 6, 7, 8, 9,10,11,12,13,14,14,15,15,16,16,17,17,18,18,4224}
        start = time.time()
        bio = BytesIO()
        io: ObjectIO = ObjectIO(bio)
        io.write_list(a)

        data = bio.getvalue()

        bio = BytesIO(data)
        io: ObjectIO = ObjectIO(bio)
        end = time.time()
        print(repr(io.read_list()))
        print("Time: " + str(end - start))

    def test8():
        b = [8192]
        a = b * 100000
        print(len(a))
        start = time.time()
        bio = BytesIO()
        io: ObjectIO = ObjectIO(bio)
        io.write_list(a)

        data = bio.getvalue()

        with open("test.qdat", "w+b") as file:
            file.write(data)
            file.flush()
            file.close()

        bio = BytesIO(data)
        io: ObjectIO = ObjectIO(bio)
        end = time.time()
        print(repr(io.read_list()))
        print("Time: " + str(end - start))

    # test1()
    # test2()
    # test3()
    # test4()
    # test5()
    # test6()
    # test7()

    test6()
