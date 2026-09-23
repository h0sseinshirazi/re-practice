# crackme02b — tumbler

**Status:** solved · **Key:** `1fDsg5Gfk` · **Solver:** [`solve.py`](solve.py)

An easier step placed between mark II and mark III. It's stripped and its strings are
hidden, but there's no chaining.

## Recon

* Strings are XOR'd with `0x79` and decoded by the helper at 0x11c0, the same pattern as gate.
* main is at 0x123e (found through `_start`).

## The check

```asm
12be  cmp  rax, 0x9            ; length 9
12ce  mov  edx, 0              ; edx = 9*i
1300  movzx eax, byte [rsi]
1303  xor  eax, 0x56
1306  add  eax, edx            ; + 9*i
1308  rol  al, 2
130b  sub  eax, 0x48
130e  cmp  al, [table + i]     ; table @ .rodata 0x2010
1316  add  edx, 9
131d  cmp  dl, 0x51            ; 0x51 = 9*9
```

`table[i] == rol8((key[i] ^ 0x56) + 9*i, 2) - 0x48`

## Inversion

Undo the steps in reverse order, one byte at a time:

```
key[i] = (ror8(table[i] + 0x48, 2) - 9*i) ^ 0x56
```

Table: `55 9c 48 b9 0d fa d5 75 ce`.

## Takeaway

This is the same shape as vault with symbols and strings removed. The skill being practised is
finding main and the table without names.
