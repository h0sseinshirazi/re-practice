# Arcade L3 — linear system

**Key:** `tqPZ6FiF8SiR` · **Solver:** [`solvers/level3.py`](solvers/level3.py)

## The check (main @ 0x11ea)

```asm
121e  cmp  [len], 0xc                      ; 12 bytes
1260  idx = row*12 + col                   ; (row*3)<<2 = row*12
127b  movzx eax, byte [0x4040 + idx]       ; M[row][col]
129c  imul eax, key[col]
129f  add  [sum], eax
12bb  movzx edx, al                        ; sum & 0xff
12c6  cmp  edx, byte [0x40d0 + row]        ; T[row]
12d8  ok = 0                               ; no early exit
```

For each of the 12 rows: `Σ M[row][col] · key[col] ≡ T[row] (mod 256)`. That's a
12×12 linear system over Z/256, with the matrix at `.data 0x4040` and the targets at `0x40d0`.

## Solving it

Gaussian elimination mod 256 needs an **odd** pivot in every column, and here it fails:
the determinant is even, so the matrix is singular mod 2 and the system has more than one solution.

The robust approach is **2-adic lifting**. First solve mod 2 (plain GF(2) elimination,
enumerating the free variables). Then for each solution `x` mod 2ᵏ, look for `y ∈ {0,1}¹²` with

```
M·(x + 2ᵏ·y) ≡ T  (mod 2ᵏ⁺¹)   ⇔   M·y ≡ (T − M·x) / 2ᵏ  (mod 2)
```

After 8 rounds there are **16 solutions mod 256**, and exactly one of them is printable ASCII.
The binary accepts any of the 16, but the others contain bytes you can't type.

`z3` does the same job in five lines (`BitVec` × 12, `solver.add(... & 0xff == t)`, plus a
printable constraint) if you'd rather not write the lifting yourself.

## Takeaway

"Linear mod 2ⁿ" isn't the same as linear algebra over a field. Check the determinant's parity
before trusting elimination.
