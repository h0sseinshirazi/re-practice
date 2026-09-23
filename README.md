# re-practice

My reverse-engineering training ground: a ladder of Linux x86-64 crackmes. It starts
with a transform you can read straight off the disassembly and ends with signed online
activation. After that comes an 8-level "arcade" with a launcher that controls progression.

The challenge binaries were generated for me by Claude as a practice ladder. Their
sources were deliberately not kept, so each one is a black box. Every walkthrough here
comes from the binary alone.

## The ladder

| Rung | Binary | Idea | Status |
|---|---|---|---|
| I | [`crackme01/vault`](crackme01/WALKTHROUGH.md) | per-byte xor/add/rol against a `.rodata` table, symbols intact | ✅ solved |
| II | [`crackme02/gate`](crackme02/WALKTHROUGH.md) | stripped, xor-hidden strings, chained state, divide-by-7 via magic multiply | ✅ solved |
| II½ | [`crackme02b/tumbler`](crackme02b/WALKTHROUGH.md) | stripped per-byte transform, no chaining | ✅ solved |
| III | `crackme03/lock` | mark III | ⬜ open |
| III′ | [`crackme03b/chain`](crackme03b/WALKTHROUGH.md) | chained state + a ptrace guard that silently poisons the seed | ✅ solved |
| IV | [`crackme04/authme`](crackme04/WALKTHROUGH.md) | "online" activation where the client trusts a constant | ✅ solved |
| V | [`crackme05/authv5`](crackme05/NOTES.md) | online activation, done right | ⬜ open |

Each solved rung has a `WALKTHROUGH.md` (recon → the check, with addresses → the inversion →
takeaway) and a `solve.py` that prints the key. The solvers are tested against the real
binaries.

## The arcade

`arcade/` is a separate 8-level ladder with a launcher. You solve level N to unlock N+1.

```
cd arcade
./arcade.py            # CLI: play
./arcade.py hint N     # tiered hints (concept → tool → region), never a key
./arcade_gui.py        # the same thing in a GTK4 window
```

The launcher checks a key by **running the real binary** and reading its exit code.
Before that it compares the binary's SHA-256 with `.checksums.json`. Patching a level
to always pass therefore doesn't count; the only way through is recovering the key.

| Level | Name | Status |
|---|---|---|
| 1 | vault-lite | ✅ [walkthrough](arcade/walkthroughs/level1.md) |
| 2 | rolling | ✅ [walkthrough](arcade/walkthroughs/level2.md) |
| 3 | linear system | ⬜ open |
| 4 | keygen | ⬜ open |
| 5 | anti-debug | ⬜ open |
| 6 | self-decrypt | ⬜ open |
| 7 | bytecode VM | ⬜ open |
| 8 | avalanche VM | ⬜ open |

## Spoiler policy

* Open rungs get no walkthrough and no hints beyond their name. The arcade's `hint`
  command is the only hint source.
* `crackme04/server.py`, `crackme05/server.py` and `crackme05/priv.pem` are the
  **server side** of the online rungs. They exist so the rungs can run, and reading them
  counts as cheating.

## Running the online rungs

```
python3 crackme04/server.py        # port 8085, then ./crackme04/authme
cd crackme05 && python3 server.py  # port 8090, then ./authv5
```

## Tooling

* **Static:** IDA (the `.i64` files are my databases) and Ghidra. objdump and readelf
  are enough for most of the early rungs.
* **Dynamic:** plain gdb. Ghidra's debugger took more time than it saved.
* **Rule:** script the inversion. Doing hex arithmetic by hand is where mistakes creep in.

## Layout

```
crackmeNN/        binary, IDA database, WALKTHROUGH.md, solve.py
crackme05/        binary + server side (server.py, priv.pem) + NOTES.md
arcade/           launcher (arcade.py, arcade_gui.py), level1–8, .checksums.json
arcade/walkthroughs/
```

Local state isn't committed: arcade progress (`.progress.json`), `__pycache__`, and Ghidra
project files.
