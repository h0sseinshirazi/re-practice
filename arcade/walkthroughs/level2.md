# Arcade L2 — rolling

**Status:** solved · **Key:** `L3mMAeBI8Bsrij` · **Solver:** [`solve_level2.py`](solve_level2.py)

## The check (`main` @ 0x11fa, symbols intact)

```asm
1242  cmp  [len], 0xe                  ; 14 characters
1264  prev = 0x5a ; ok = 1
129d  edx = c * A                      ; A @ 0x4040 = 0xf7
12a6  edx += B                         ; B @ 0x4044 = 0xfb
12b4  eax = i*i + edx ; & 0xff
12ca  out ^= prev ; prev = out
12e4  cmp out, T[i]                    ; T @ 0x4030, 14 bytes
12fa  ok = 0 on mismatch (keeps looping — no early exit)
```

`T[i] == ((key[i]*A + B + i*i) & 0xFF) ^ prev`, where `prev` is the previous output (the
seed is 0x5a).

## Inversion

When the key is right, each output equals `T[i]`, so `prev` is just `T[i-1]`. Undo the XOR,
subtract `B + i²`, then undo the multiply. That last step is the new part: **multiply by the
modular inverse of A**. Because A (0xf7) is odd, it has an inverse mod 256.

```python
A_INV = pow(0xF7, -1, 256)
key[i] = (((T[i] ^ prev) - B - i*i) * A_INV) & 0xFF
```

## Takeaway

Multiplication mod 2⁸ is reversible whenever the multiplier is odd. `pow(a, -1, m)` does it
in one line.
