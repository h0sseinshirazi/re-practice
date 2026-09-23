# crackme02 — gate (mark II)

**Status:** solved · **Key:** `n0_symb0ls_here` · **Solver:** [`solve.py`](solve.py)

## What changed from mark I

* **Stripped.** There's no `main` symbol. Find it through `_start`: the `lea rdi, [rip+…]`
  just before `__libc_start_main` points at main (0x121e).
* **No readable strings.** The messages sit in `.data` XOR'd with `0x5A` and are decoded
  just before printing by a helper at 0x11a0 (`xor edx, 0x5a` in a loop, then `puts`).
  That's why `strings` shows only `key> `.
* **Chained state.** Each byte's check depends on every byte before it.

## The check (main @ 0x121e)

```asm
129e  cmp  rax, 0xf                       ; length 15
12ab  mov  r8d, 0x1f                      ; state = 0x1f
12b6  movabs rbx, 0x2492492492492493      ; magic reciprocal → i / 7
...   rcx = i - 7*(i/7) + 1               ; rot = i % 7 + 1
12ce  xor  edi, r8d                       ; c ^ state
12fb  rol  dil, cl
12fe  add  edi, 0x3b
1301  cmp  dil, [table + i]               ; table @ .rodata 0x2010
1307  state = state*32 - state + c        ; shl 5 / sub → state*31 + c
```

The multiply by `0x2492…93` followed by shifts is how the compiler divides by 7 without a
`div`. Recognising it is most of the work here.

Per position: `table[i] == rol8(key[i] ^ (state & 0xFF), i%7 + 1) + 0x3B`, then
`state = state*31 + key[i]`.

## Inversion

Go left to right. Byte *i* needs the state, and the state needs bytes 0..i-1, which you
already have:

```
key[i] = ror8(table[i] - 0x3B, i%7 + 1) ^ (state & 0xFF)
state  = state*31 + key[i]
```

Only the low byte of the state feeds the XOR, and the low byte of `state*31 + c` depends
only on the old low byte. So 8-bit arithmetic gives the same answer.

## Takeaway

Chaining doesn't make a transform harder to invert. It only forces the order. Magic-number
division is worth recognising on sight.
