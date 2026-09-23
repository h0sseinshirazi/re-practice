# crackme01 — vault (mark I)

**Status:** solved · **Key:** `gh0st_pr0t0!` · **Solver:** [`solve.py`](solve.py)

## Recon

```
$ file vault      → ELF 64-bit PIE, dynamically linked, not stripped
$ nm vault | grep -v ' _'
00000000000011a0 T main
00000000000020c8 r vault
```

The binary isn't stripped, and a `.rodata` symbol called `vault` is a big giveaway.
`strings` shows the banner and the GRANTED/DENIED messages, but no key.

## The check (`main` @ 0x11a0)

```asm
1224  call strlen
1229  cmp  rax, 0xc            ; key is 12 bytes
1232  lea  rcx, [vault]        ; expected table
1239  mov  edx, 0              ; edx = i*7
1240  movzx eax, byte [rsi]    ; c = key[i]
1243  xor  eax, 0x5a
1246  add  eax, edx            ; + i*7
1248  rol  al, 3
124b  cmp  al, byte [rcx]      ; == vault[i] ?
1253  add  edx, 7
125a  cmp  dl, 0x54            ; 0x54 = 12*7 → loop 12 times
```

So for each position: `vault[i] == rol8((key[i] ^ 0x5A) + 7*i, 3)`.

## Inversion

Every step can be undone, and positions don't depend on each other, so each byte is solved on its own:

```
key[i] = (ror8(vault[i], 3) - 7*i) ^ 0x5A        (all mod 256)
```

Table at 0x20c8: `e9 c9 c3 f1 52 41 a2 ca 15 6b 85 46`.

## Takeaway

When there are symbols, use them. gdb (`x/12xb &vault`) or `objdump -s -j .rodata` gets the
table in seconds. Script the inversion instead of doing hex arithmetic by hand.
