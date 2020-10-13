#!/usr/bin/env python
"""Hex Utilities."""
import re
from binascii import unhexlify


def cord(x):
    """Return ord(x) or x if x is integer."""
    return ord(x) if not isinstance(x, int) else x


def hexdump(src, length=16, digits=4):
    """Pretty Hex Dumping Function.

    Directly taken from http://code.activestate.com/recipes/142812-hex-dumper/.
    """
    result = []
    # digits = 4 if isinstance(src, str) else 2
    # digits = 4
    for i in range(0, len(src), length):
        s = src[i: i + length]
        hexa = b" ".join([b"%0*X" % (digits, cord(x)) for x in s])
        if isinstance(src, str):
            text = b"".join(
                [bytes(x, "utf8") if 0x20 <= ord(x)
                 < 0x7F else b"." for x in s]
            )
        else:
            text = b"".join(
                [
                    bytes(chr(cord(x)), "utf8") if 0x20 <= cord(
                        x) < 0x7F else b"."
                    for x in s
                ]
            )
        result.append(
            (b"%0" + b"%dX:" % (digits) + b" %-*s |%s|")
            % (i, length * (2 + 1) + 1, hexa, text)
        )
    return b"\n".join(result)


def slice_hexdump(hexd: bytes) -> str:
    """Find Slice of byte string from hexdump output and return the deocded str."""
    stm = re.search(":", hexd.decode())
    edm = re.search(r"\|", hexd.decode())
    if not stm:
        st = 0
    if not edm:
        ed = -1
    st = stm.start() + 1
    ed = edm.start()
    return hexd[st:ed].decode()


def hex2bin(x):
    """Return Byte string from Hex String."""
    return unhexlify(str.encode(x.replace(" ", "").replace("\n", "")))


def printbin(x):
    """Print decoded string from byte x."""
    print(x.decode())


def hd(f, length=16, digits=4):
    """Hexdump the Given Filename, using blocksize=length and digits=digits."""
    with open(f, "rb") as fl:
        print(hexdump(fl.read(), length=length, digits=digits).decode())


if __name__ == "__main__":
    import argparse
    import sys

    parser = argparse.ArgumentParser(prog="HexDump")
    parser.add_argument(
        "-f",
        "--file",
        action="store",
        dest="filename",
        help="file to hexdump.",
    )
    parser.add_argument(
        "-b",
        "--block-size",
        action="store",
        dest="length",
        type=int,
        default=16,
        help="Chunk Size to Dump file in default 16 bytes.",
    )
    parser.add_argument(
        "-d",
        "--digits",
        action="store",
        dest="digits",
        type=int,
        default=4,
        help="Number of leading zeros to pad hex numbers with.",
    )
    args = parser.parse_args()
    if not args.filename:
        print("Filename path is required!!.")
        sys.exit(0)
    hd(args.filename, args.length, args.digits)
