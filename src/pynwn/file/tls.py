import re
import struct
import os

ENTRY_RE = re.compile('^<(\d+)><\d*>:(.+)')

from pynwn.file.tlk import Tlk
from pynwn.util import get_encoding


class Tls:
    """The Tls file format was created by Meaglyn.
    """

    def __init__(self, filename=None):
        self.entries = {}
        cur_line = ""
        cur_index = None
        if filename is not None and os.path.exists(filename) and os.path.isfile(filename):
            with open(filename) as f:
                for line in f.read().splitlines():
                    if len(line) and line[0] == '#':
                        continue
                    m = ENTRY_RE.match(line)
                    if m:
                        if cur_index is not None:
                            self.entries[cur_index] = cur_line
                        cur_index = int(m.group(1))
                        cur_line = m.group(2)

                    else:
                        cur_line += '\n' + line

                if cur_index is not None:
                    self.entries[cur_index] = cur_line

    def __len__(self):
        return max(self.entries.keys()) + 1

    def __setitem__(self, i, val):
        assert (isinstance(val, str))
        self.entries[i] = val

    def __getitem__(self, i):
        if i not in self.entries:
            return ""
        return self.entries[i]

    def inject(self, other):
        for i in range(len(other)):
            n = other[i]
            if len(n):
                self.entries[i] = n

    def __str__(self):
        res = ["#TLS V1.0 Uncompiled TLK source#"]
        for i in range(len(self)):
            if i in self.entries:
                res.append("<%d><%d>:%s" % (i, i + 0x01000000, self.entries[i]))
        return '\n'.join(res)

    def write(self, io):
        io.write("#TLS V1.0 Uncompiled TLK source#\n")
        for i in range(len(self) + 1):
            n = self[i]
            if len(n):
                io.write("<%d><%d>:%s\n" % (i, i + 0x01000000, n))

    def write_tlk(self, io, lang):
        header = struct.pack("4s 4s I I I",
                             b'TLK ',
                             b'V3.0',
                             lang,
                             len(self),
                             Tlk.HEADER_SIZE + len(self) * Tlk.DATA_ELEMENT_SIZE)
        io.write(header)

        offset = 0
        strings = []

        # Always inject Bad Strref
        if not self[0]:
            self[0] = 'Bad Strref'

        for i in range(len(self)):
            n = self[i]
            entries = struct.pack("I 16s I I I I f",
                                  0x1 if len(n) else 0,
                                  b"",
                                  0,
                                  0,
                                  offset if len(n) else 0,
                                  len(n),
                                  0)
            io.write(entries)
            if len(n):
                offset += len(n)
                strings.append(n)
        io.write(bytearray(''.join(strings), get_encoding()))
