#!/usr/bin/env python3
"""authv5: two-byte-site patch. Writes authv5.patched next to the original.

  0x1518  je 0x15e6        (reply == "DENY" -> refuse)   -> 6x NOP
  0x163c  cmove rdi, rax   (pick ACTIVATED if verify==1) -> mov rdi, rax ; nop
File offset == vaddr for .text in this PIE (LOAD 0x1000 -> 0x1000).
"""
import os, stat, sys
here = os.path.dirname(os.path.abspath(__file__))
src = os.path.join(here, "..", "..", "crackme05", "authv5")
dst = src + ".patched"
b = bytearray(open(src, "rb").read())

def patch(off, old, new):
    old, new = bytes.fromhex(old), bytes.fromhex(new)
    assert b[off:off+len(old)] == old, f"unexpected bytes at {off:#x}"
    b[off:off+len(new)] = new

patch(0x1518, "0f84c8000000", "909090909090")
patch(0x163c, "480f44f8",     "4889c790")
open(dst, "wb").write(b)
os.chmod(dst, os.stat(src).st_mode | stat.S_IXUSR)
print("wrote", os.path.relpath(dst))
