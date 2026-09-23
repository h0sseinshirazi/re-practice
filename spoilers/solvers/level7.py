#!/usr/bin/env python3
"""L7 bytecode VM: per lane XOR X, ADD A, ROL R, CMP C  ->  key = (ror(C,R) - A) ^ X."""
import os
ARCADE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "arcade")

def rd(level, vaddr, n):
    """Read n bytes at a .data virtual address (file offset = vaddr - 0x1000)."""
    with open(os.path.join(ARCADE, f"level{level}"), "rb") as f:
        f.seek(vaddr - 0x1000)
        return f.read(n)

X, A, R, C = (rd(7, a, 16) for a in (0x4030, 0x4040, 0x4050, 0x4060))
ror = lambda x, n: ((x >> n) | (x << (8 - n))) & 0xFF
print(bytes(((ror(c, r) - a) & 0xFF) ^ x for x, a, r, c in zip(X, A, R, C)).decode())
