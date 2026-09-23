#!/usr/bin/env python3
"""chain: invert the chained check. Initial state is 0x7c when NOT traced."""
TABLE = bytes.fromhex("94e89a2dead9b30df3f2c28a8a192e")  # .rodata 0x2010
ror = lambda x, n: ((x >> n) | (x << (8 - n))) & 0xFF

state, key = 0x7C, bytearray()
for i, t in enumerate(TABLE):
    c = ror((t - 0x74) & 0xFF, i % 7 + 1) ^ state
    key.append(c)
    state = (state * 31 + c) & 0xFF
print(key.decode())
