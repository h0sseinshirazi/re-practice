# Arcade L7 — bytecode VM

**Key:** `MttgAf4827hdeHKj` · **Solver:** [`solvers/level7.py`](solvers/level7.py)

## The program (built at 0x11ea)

Before reading input, main calls a builder that writes the bytecode into `.bss 0x40a0`:
`01 02 03 04`, repeated 16 times, followed by `00`. It's one 4-instruction program per key byte.

## The ISA (dispatcher @ 0x12ec)

| Op | Semantics | Operand table |
|---|---|---|
| `01` | `acc = key[lane] ^ X[lane]` | X @ 0x4030 |
| `02` | `acc = (acc + A[lane]) & 0xff` | A @ 0x4040 |
| `03` | `acc = rol8(acc, R[lane])` (shl/sar pair) | R @ 0x4050 |
| `04` | `ok &= acc == C[lane]` then `lane++` | C @ 0x4060 |
| `00` | halt | |

The key length is 16 (`cmp …, 0x10`). There's no early exit.

## Inversion

Run each lane backwards: `key = (ror8(C, R) − A) ^ X`.

Undo the steps in the reverse order the VM applies them. XOR comes before ADD on the way in,
so the subtraction happens before the XOR on the way out. Swapping them gives
non-ASCII output, which is the quickest sign you've got the order wrong.

## Takeaway

For VM crackmes: find the dispatcher, list the opcodes, dump the program. After that it's an
ordinary transform, and here every lane is independent.
