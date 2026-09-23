# ⚠ Spoilers

Everything in this folder gives away rungs that the main README leaves open: arcade
levels 3–8 and crackme05/authv5. Each file has the full method, the addresses, and the key.
If you want to solve them yourself, stop here and run `./arcade.py hint N`.

| Rung | Idea | Walkthrough | Solver |
|---|---|---|---|
| Arcade L3 | 12×12 linear system mod 256 | [level3.md](level3.md) | [`solvers/level3.py`](solvers/level3.py) |
| Arcade L4 | name → serial keygen | [level4.md](level4.md) | [`solvers/level4.py`](solvers/level4.py) |
| Arcade L5 | three anti-debug guards over an XOR check | [level5.md](level5.md) | [`solvers/level5.py`](solvers/level5.py) |
| Arcade L6 | checker copied to an RWX page, called through a pointer | [level6.md](level6.md) | [`solvers/level6.py`](solvers/level6.py) |
| Arcade L7 | bytecode VM | [level7.md](level7.md) | [`solvers/level7.py`](solvers/level7.py) |
| Arcade L8 | chained "avalanche" VM + ptrace | [level8.md](level8.md) | [`solvers/level8.py`](solvers/level8.py) |
| crackme05 | Ed25519-signed activation | [authv5.md](authv5.md) | [`solvers/patch_authv5.py`](solvers/patch_authv5.py) |

The arcade solvers read their constants straight out of the level binaries, and every
key has been checked through the launcher's own verifier (`arcade.run_check`).
