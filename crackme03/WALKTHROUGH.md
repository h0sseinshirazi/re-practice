# crackme03 — lock (mark III)

**Status:** solved · **Key:** `4?tp&n9RDAq-#O5` · **Solver:** [`solve.py`](solve.py)

Mark III is mark II with three additions: a keystream generated at runtime, a ptrace guard,
and a mismatch check that never branches. ([chain](../crackme03b/WALKTHROUGH.md) is the same
rung without the keystream, built as a stepping stone.)

## Recon

* Stripped, with strings XOR'd with `0x1c` (decoder at 0x11c0). main is at 0x123e.
* `ptrace` appears in the imports. The table at `.rodata 0x2010` is 15 bytes, but
  comparing against it directly gets you nowhere, because it's masked.

## The seed and the guard

```asm
12d0  call ptrace                  ; PTRACE_TRACEME
12d5  sar  rax, 0x3f               ; -1 if already traced
12d9  and  eax, 0xffff6dc5
12de  lea  ebx, [rax+0x5ba6ba]     ; seed = 0x5ba6ba (normal) / 0x5b147f (under gdb)
12ee  cmp  rax, 0xf                ; length 15
```

As in chain, the guard doesn't announce anything. It moves the seed, and under a debugger
every keystream byte comes out wrong.

## The keystream (0x1340)

```asm
1340  eax = x ^ (x << 15)
1349  eax ^= eax >> 19
1350  x   = eax ^ (eax << 5)
1355  ks[i] = (x >> 11) & 0xff     ; 15 bytes
```

This is a xorshift-style 32-bit PRNG. It's deterministic, so reimplement it and seed it with 0x5ba6ba.

## The check (0x1381)

```asm
1375  state = 0xfffffffd                     ; only the low byte (0xfd) matters
1384  r = state ^ key[i]
13ae  rol  r, i%7 + 1                        ; divide-by-7 magic again
13b6  a = ks[i] ^ table[i]
13ba  b = ks[i] + r
13bd  mismatch |= (a ^ b) & 0xff             ; no early exit
13c5  state = state*41 + key[i]              ; lea s+s*4 → lea s+5s*8 = 41s
```

A position passes when `(ks[i] + rol8(state ^ key[i], i%7+1)) & 0xFF == ks[i] ^ table[i]`.

## Inversion

Left to right, the same shape as gate and chain with one more layer to peel off:

```
r      = ((ks[i] ^ table[i]) - ks[i]) & 0xFF
key[i] = ror8(r, i%7 + 1) ^ state
state  = (state*41 + key[i]) & 0xFF        # start at 0xfd
```

## Takeaway

A PRNG mask is only as secret as its seed, and here the seed is a constant. Once the
generator is reimplemented, mark III reduces to mark II. Read the seed statically; under
gdb, ptrace hands you the wrong one.
