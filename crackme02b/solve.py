#!/usr/bin/env python3
"""tumbler: undo sub/rol/add/xor per byte (no chaining)."""
TABLE = bytes.fromhex("559c48b90dfad575ce")  # .rodata 0x2010
ror = lambda x, n: ((x >> n) | (x << (8 - n))) & 0xFF

print(bytes((((ror((t + 0x48) & 0xFF, 2)) - 9 * i) & 0xFF) ^ 0x56
            for i, t in enumerate(TABLE)).decode())
