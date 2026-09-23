# Arcade L5 — anti-debug

**Key:** `WGciZMXfXt3knQ` · **Solver:** [`solvers/level5.py`](solvers/level5.py)

## Three guards (main @ 0x133f)

| Where | Guard | Trips when |
|---|---|---|
| 0x123a | reads `/proc/self/status` and `atoi`s the `TracerPid:` line | anything is attached |
| 0x1394 | `ptrace(PTRACE_TRACEME)` < 0 | a debugger already traces us |
| 0x1321 / 0x1499 | `rdtsc` before and after the check; delta > `0x1e8480` (2,000,000 cycles) | you single-step or break inside the loop |

Each guard prints `nope.` and exits with code 2.

## The check itself

```asm
13d1  cmp  [len], 0xe                ; 14 bytes
1433  ecx = key[i] ^ K               ; K @ 0x4060 = 0x54
1441  ecx ^= (i*13) & 0xff           ; (i*3)<<2 + i = 13i
1453  cmp  ecx, T[i]                 ; T @ 0x4050
```

`key[i] = T[i] ^ 0x54 ^ (13·i)`.

## Takeaway

The guards only guard a debugger session. Read statically and you never trigger them.
To debug it anyway: `catch syscall ptrace` and set `rax=0`, then break *after* the second
`rdtsc`, or patch a copy of the binary.
