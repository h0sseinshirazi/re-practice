#!/usr/bin/env python3
"""lock (mark III): regenerate the xorshift keystream, then invert the chained check."""
TABLE = bytes.fromhex("932e5cc2a831483e8152e869c545f5")  # .rodata 0x2010
ror = lambda x, n: ((x >> n) | (x << (8 - n))) & 0xFF
M32 = 0xFFFFFFFF

def keystream(seed, n):
    x, out = seed, []
    for _ in range(n):
        x ^= (x << 15) & M32
        x ^= x >> 19
        x ^= (x << 5) & M32
        out.append((x >> 11) & 0xFF)
    return out

ks = keystream(0x5BA6BA, 15)       # seed when NOT traced
state, key = 0xFD, bytearray()     # 0xfffffffd, low byte
for i, t in enumerate(TABLE):
    mixed = ((ks[i] ^ t) - ks[i]) & 0xFF
    c = ror(mixed, i % 7 + 1) ^ state
    key.append(c)
    state = (state * 41 + c) & 0xFF
print(key.decode())
