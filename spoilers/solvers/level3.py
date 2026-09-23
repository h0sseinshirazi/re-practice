#!/usr/bin/env python3
"""L3 linear system: solve M·x ≡ T (mod 256) by lifting one bit at a time."""
import itertools
import os
ARCADE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "arcade")

def rd(level, vaddr, n):
    """Read n bytes at a .data virtual address (file offset = vaddr - 0x1000)."""
    with open(os.path.join(ARCADE, f"level{level}"), "rb") as f:
        f.seek(vaddr - 0x1000)
        return f.read(n)

N = 12
M = [list(rd(3, 0x4040 + N * i, N)) for i in range(N)]   # 12x12 matrix @ 0x4040
T = list(rd(3, 0x40D0, N))                               # targets @ 0x40d0

def gf2_all(A, b):
    """Every y in GF(2)^N with A·y = b (mod 2)."""
    rows = [[a & 1 for a in r] + [bb & 1] for r, bb in zip(A, b)]
    piv, r = [], 0
    for c in range(N):
        p = next((i for i in range(r, N) if rows[i][c]), None)
        if p is None:
            continue
        rows[r], rows[p] = rows[p], rows[r]
        for i in range(N):
            if i != r and rows[i][c]:
                rows[i] = [x ^ y for x, y in zip(rows[i], rows[r])]
        piv.append(c); r += 1
    if any(rows[i][N] for i in range(r, N)):
        return []
    free = [c for c in range(N) if c not in piv]
    out = []
    for fv in itertools.product((0, 1), repeat=len(free)):
        y = [0] * N
        for c, v in zip(free, fv):
            y[c] = v
        for i, c in enumerate(piv):
            y[c] = rows[i][N] ^ (sum(rows[i][f] & y[f] for f in free) & 1)
        out.append(y)
    return out

sols = [[0] * N]
for k in range(8):                       # solutions mod 2^(k+1) from those mod 2^k
    sols = [[v + (yy << k) for v, yy in zip(x, y)]
            for x in sols
            for y in gf2_all(M, [((t - sum(m * v for m, v in zip(row, x))) >> k) & 1
                                 for row, t in zip(M, T)])]
printable = [bytes(s) for s in sols if all(33 <= c < 127 for c in s)]
print(f"{len(sols)} solutions mod 256, printable: {[p.decode() for p in printable]}")
