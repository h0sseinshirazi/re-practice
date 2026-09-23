# Arcade L6 — self-decrypt

**Key:** `agTx2L5MTVKwdW` · **Solver:** [`solvers/level6.py`](solvers/level6.py)

## What main does (0x1268)

```asm
1278  sysconf(_SC_PAGESIZE)
1281  size = 0x1261 - 0x11fa             ; length of the checker function
12ca  mmap(NULL, round_up(size), PROT_READ|WRITE|EXEC (7), MAP_PRIVATE|ANON (0x22), -1, 0)
1310  memcpy loop: checker → the new page
1397  call r8                            ; checker(key, T @ 0x4030, 14, K @ 0x4040)
```

The "decrypt" is only a relocation. The checker at **0x11fa** is copied byte for byte, so it's
sitting in the file and a disassembler shows it as a normal function that nothing calls directly:

```asm
1235  movzx eax, byte [T + i]
123b  xor  eax, K                    ; K = 0x57
123e  xor  eax, key[i]
1243  test eax, eax → fail on first mismatch
```

`key[i] = T[i] ^ 0x57`. The table is 14 bytes, and its **last byte is 0x00**, which gives
`'W'`. If your answer is 13 characters, you stopped reading at what looked like a
string terminator.

## Takeaway

When code runs from an `mmap`'d page, work out where its bytes come from before you
fight the runtime. Here the source is plain code in `.text`. In a real packer you'd break
on the `call r8` and dump the page.
