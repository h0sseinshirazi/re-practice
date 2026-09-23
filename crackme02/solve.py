#!/usr/bin/env python3
"""gate (mark II): invert the chained per-byte check, left to right."""
TABLE = bytes.fromhex("1db73019d8b5c08da86e5564bb919d")  # .rodata 0x2010
ror = lambda x, n: ((x >> n) | (x << (8 - n))) & 0xFF

state, key = 0x1F, bytearray()
for i, t in enumerate(TABLE):
    c = ror((t - 0x3B) & 0xFF, i % 7 + 1) ^ (state & 0xFF)
    key.append(c)
    state = (state * 31 + c) & 0xFFFFFFFF
print(key.decode())
