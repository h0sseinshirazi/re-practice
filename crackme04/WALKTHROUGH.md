# crackme04 — authme (simulated online activation)

**Status:** solved · **Grant token:** `GR4NT-R4X53GC1XM` · **Solver:** [`solve.py`](solve.py)

## How it works (main @ 0x1200)

1. Reads a license key.
2. `socket` / `connect` to 127.0.0.1, port `0x951f` in network order, which is **8085**.
3. `dprintf(fd, "AUTH %s\n", key)`, then reads one reply line.
4. Decodes a 16-byte blob at `.rodata 0x20b0` with `xor 0x50` onto the stack.
5. `strcmp(reply, decoded)`. If they're equal, it prints `*** ACTIVATED ***`.

## The flaw

The client already holds the answer it's waiting for. The license key is never checked
locally. It's forwarded to the server, and the only thing that matters is whether the
reply matches a constant that sits in the binary.

```
token = bytes(b ^ 0x50 for b in rodata[0x20b0:0x20c0])  →  GR4NT-R4X53GC1XM
```

Once you have the token you don't need a valid license. Run your own server on 8085 that
replies with the token and any key activates:

```
python3 solve.py --serve     # terminal 1
./authme                     # terminal 2, type anything
```

## Takeaway

This is the classic mistake in "online" DRM. If the client can check the server's answer
with only what it ships, you can forge the answer. [crackme05](../crackme05/NOTES.md)
fixes it.

> `server.py` here is a reconstruction (2026-09-24). The original was overwritten,
> so it isn't needed to solve the rung, only to play it "legitimately".
