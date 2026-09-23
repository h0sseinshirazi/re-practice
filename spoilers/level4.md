# Arcade L4 — keygen

**Solver:** [`solvers/level4.py`](solvers/level4.py) · e.g. `USER-ABC123` → `0000-67D8-F9F9-7715`

There's no fixed key. The launcher runs `level4 <random name>` and reads a serial on stdin,
so you need a keygen.

## The serial function (0x121a)

```asm
1239  h = 0x1505                         ; 5381, the djb2 seed
124d  h = (h + (h << 5)) ^ c             ; h*33 ^ c — djb2, xor variant, 32-bit
1276  imul rax, rax, 0x83e3              ; v = (u64)h * 0x83e3
1280  shl  rdx, 0xd                     ; ^ ((u64)h << 13)
1287  xor  al, 0xae                      ; low byte ^ 0xae
1296  16 nibbles, high to low → "0123456789ABCDEF"[…]   (table @ .rodata 0x201a)
12e0  insert '-' every 4 chars           ; XXXX-XXXX-XXXX-XXXX
```

main (0x1356) takes the name from `argv[1]`, or prompts `name:` if there isn't one. It then
reads the serial and compares it with `strcmp` against `serial(name)`.

## Keygen

Reimplement it exactly. The details that matter:
* `h` wraps at **32 bits** (it lives in a `DWORD`), but the mix is done in **64 bits**.
* `h` < 2³², so `h·0x83e3` < 2⁴⁸ and `h<<13` < 2⁴⁵. The top 16 bits are always
  zero, which means **every serial starts with `0000-`**. That's a quick sanity check for your keygen.

## Takeaway

A keygen is a straight port. Match the integer widths exactly, because most wrong keygens are
wrong because of truncation.
