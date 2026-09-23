# Arcade L1 — vault-lite

**Status:** solved · **Key:** `Yl6DX6Cncvh`

This is rung zero. `main` calls `strcmp` against a global called `PASSWORD` (`.data` 0x4038),
and the string is stored in plain text:

```
$ strings -n 6 level1 | head
Yl6DX6Cncvh
== L1 : vault-lite ==
```

The binary's own success message says it: *"try `strings` next time to skip the guessing."*
Always run `strings` before opening a disassembler.
