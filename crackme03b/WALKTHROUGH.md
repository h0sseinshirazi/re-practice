# crackme03b — chain

**Status:** solved · **Key:** `lm9GXXUF#hEthsf` · **Solver:** [`solve.py`](solve.py)

Mark III without the encryption layer: chained state, a ptrace guard, and a plaintext table.

## Recon

* Stripped, with strings XOR'd with `0x60` (decoder at 0x11c0). main is at 0x123e.
* `ptrace` appears in the imports. That's the first thing to look at.

## The anti-debug trick

```asm
12cf  call ptrace              ; ptrace(PTRACE_TRACEME, 0, 1, 0)
12d4  sar  rax, 0x3f           ; -1 if it failed (already traced), else 0
12d8  and  eax, 0x45
12db  lea  ebx, [rax+0x7c]     ; state = 0x7c   (normal)
                               ; state = 0xc1   (under a debugger)
```

It never says "debugger detected". It quietly changes the **initial state**. Under gdb the
right key is rejected, and any constants you read out of registers are wrong. Read
the state statically as **0x7c**.

## The check

```asm
12e6  cmp  rax, 0xf                    ; length 15
1305  dl = state ^ key[i]
130c  imul … 0x92492493 …              ; i / 7 → rot = i%7 + 1
1330  rol  dl, cl
1332  add  edx, 0x74
1335  xor  dl, [table + i]             ; table @ .rodata 0x2010
133c  or   r8d, edx                    ; accumulate mismatches — no early exit
133f  state = (state*31 + key[i]) & 0xff
1358  test r8d, r8d                    ; all positions must be 0
```

Two details:

* The comparison is **XOR-and-OR-accumulate** rather than `cmp`/`jne`, so no branch tells
  you which byte failed. Brute-forcing byte by byte by watching control flow doesn't work.
* The state is kept in `al`, so it's 8-bit.

Per position: `table[i] == rol8(key[i] ^ state, i%7 + 1) + 0x74`.

## Inversion

```
key[i] = ror8(table[i] - 0x74, i%7 + 1) ^ state
state  = (state*31 + key[i]) & 0xFF        # start at 0x7c
```

Constants: length 15 · initial state 0x7c · rotate mod 7 · add 0x74 · multiplier 31.

## Takeaway

Static analysis doesn't trip the guard at all. When a binary acts differently under a debugger,
ask what the debugger changed, not just whether it's being detected.
