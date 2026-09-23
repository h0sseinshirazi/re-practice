#!/usr/bin/env python3
"""L4 keygen: name -> serial.   usage: level4.py USER-XXXXXX"""
import sys

def serial(name: str) -> str:
    h = 5381                                   # djb2, xor variant, 32-bit
    for c in name.encode():
        h = ((h * 33) & 0xFFFFFFFF) ^ c
    v = ((h * 0x83E3) ^ (h << 13)) ^ 0xAE      # 64-bit mix, low byte ^ 0xae
    digits = "".join("0123456789ABCDEF"[(v >> (4 * (15 - i))) & 0xF] for i in range(16))
    return "-".join(digits[i:i + 4] for i in range(0, 16, 4))

print(serial(sys.argv[1] if len(sys.argv) > 1 else input("name: ")))
