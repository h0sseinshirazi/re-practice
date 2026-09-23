#!/usr/bin/env python3
"""L5 anti-debug: ignore the guards, read the check: key[i] = T[i] ^ K ^ (13*i)."""
import os
ARCADE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "arcade")

def rd(level, vaddr, n):
    """Read n bytes at a .data virtual address (file offset = vaddr - 0x1000)."""
    with open(os.path.join(ARCADE, f"level{level}"), "rb") as f:
        f.seek(vaddr - 0x1000)
        return f.read(n)

T, K = rd(5, 0x4050, 14), rd(5, 0x4060, 1)[0]
print(bytes(t ^ K ^ ((13 * i) & 0xFF) for i, t in enumerate(T)).decode())
