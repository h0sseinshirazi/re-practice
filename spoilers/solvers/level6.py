#!/usr/bin/env python3
"""L6 self-decrypt: the copied checker compares key[i] == T[i] ^ K."""
import os
ARCADE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "arcade")

def rd(level, vaddr, n):
    """Read n bytes at a .data virtual address (file offset = vaddr - 0x1000)."""
    with open(os.path.join(ARCADE, f"level{level}"), "rb") as f:
        f.seek(vaddr - 0x1000)
        return f.read(n)

T, K = rd(6, 0x4030, 14), rd(6, 0x4040, 1)[0]
print(bytes(t ^ K for t in T).decode())
