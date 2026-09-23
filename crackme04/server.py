#!/usr/bin/env python3

# Bytes from .rodata (vault array, 12 bytes / strlen == 12)
VAULT = [0xE9, 0xC9, 0xC3, 0xF1, 0x52, 0x41, 0xA2, 0xCA, 0x15, 0x6B, 0x85, 0x46]


def ror8(x: int, n: int) -> int:
    """Rotate an 8-bit value right by n bits."""
    x &= 0xFF
    n &= 7
    return ((x >> n) | (x << (8 - n))) & 0xFF


def solve(vault: list[int]) -> str:
    result = []
    for i, vb in enumerate(vault):
        v5 = (i * 7) & 0xFF
        tmp = ror8(vb, 3)          # undo ROL1(x, 3)
        inner = (tmp - v5) & 0xFF  # undo "+ v5"
        ib = inner ^ 0x5A          # undo "^ 0x5A"
        result.append(ib)
    return bytes(result).decode('ascii')


if __name__ == "__main__":
    key = solve(VAULT)
    print(f"Recovered key: {key}")