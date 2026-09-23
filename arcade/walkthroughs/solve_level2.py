#!/usr/bin/env python3
"""arcade L2 (rolling): out = ((c*A + B + i*i) & 0xff) ^ prev; prev = out."""
T = bytes.fromhex("15240e418304c95211ebbfcd17fd")  # symbol T, .data 0x4030
A, B, SEED = 0xF7, 0xFB, 0x5A                      # symbols A, B; seed from main
A_INV = pow(A, -1, 256)                            # A is odd -> invertible mod 256

prev, key = SEED, ""
for i, t in enumerate(T):
    key += chr((((t ^ prev) - B - i * i) * A_INV) & 0xFF)
    prev = t
print(key)
