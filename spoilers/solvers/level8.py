#!/usr/bin/env python3
"""L8 avalanche VM: out = rol((in ^ X ^ prev) * M, i%7+1), prev = out. Solve left to right."""
import os
ARCADE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "arcade")

def rd(level, vaddr, n):
    """Read n bytes at a .data virtual address (file offset = vaddr - 0x1000)."""
    with open(os.path.join(ARCADE, f"level{level}"), "rb") as f:
        f.seek(vaddr - 0x1000)
        return f.read(n)

X, M, T = rd(8, 0x4030, 18), rd(8, 0x4050, 18), rd(8, 0x4070, 18)
ror = lambda x, n: ((x >> n) | (x << (8 - n))) & 0xFF
prev, key = 0xA7, bytearray()
for i in range(18):
    v = (ror(T[i], i % 7 + 1) * pow(M[i], -1, 256)) & 0xFF   # every M[i] is odd
    key.append(v ^ X[i] ^ prev)
    prev = T[i]
print(key.decode())
