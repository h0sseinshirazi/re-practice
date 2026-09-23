# Arcade L8 — avalanche VM (boss)

**Key:** `G7odJFLHGuM3IbTM0d` · **Solver:** [`solvers/level8.py`](solvers/level8.py)

## Guard

`ptrace(PTRACE_TRACEME)` at 0x122d. If it fails, the level prints `nope.` and exits with code 2.
Nothing else, so static reading is unaffected.

## The check (main @ 0x11fa)

```asm
126a  cmp  [len], 0x12              ; 18 bytes
1287  prev = 0xa7
12cc  v = key[i] ^ X[i]             ; X @ 0x4030
12ce  v ^= prev
12f5  v = (v * M[i]) & 0xff         ; M @ 0x4050
1310  imul … 0x92492493             ; i % 7 again
1332  r = i%7 + 1
134b  v = rol8(v, r)
1387  cmp  v, T[i]                  ; T @ 0x4070 (mismatch clears ok, no early exit)
1399  prev = v
```

Each output feeds `prev` into the next byte, so a one-byte change ripples through every later
comparison. That ripple is the "avalanche".

## Inversion

When the key is right, `prev` for byte *i* is just `T[i−1]`, a value you already have. So the
avalanche goes away and every byte can be solved on its own:

```
v      = ror8(T[i], i%7 + 1)
v      = v · M[i]⁻¹  (mod 256)      # all 18 multipliers are odd, so pow(M, -1, 256) exists
key[i] = v ^ X[i] ^ prev           # prev = 0xa7, then T[i-1]
```

## Takeaway

Chaining makes brute force harder, but it doesn't make inversion harder. When the chained
value is the thing being compared, the comparison table gives you the whole chain.
It's the same lesson as gate and chain, combined with L2's modular inverse.
