#!/usr/bin/env python3
"""
crackme arcade — a progression of reversing challenges.

Each level is a separate binary in this directory. Solve level N to unlock
N+1. The launcher checks your key by running the real binary, so patching a
binary to always-succeed won't count: the launcher verifies the file is
unmodified first. Analyse the binaries however you like (objdump, Ghidra,
gdb, r2) — this menu is only the gate and the hint desk.

  ./arcade.py            play
  ./arcade.py hint N     show the next hint for level N (nudges, never a key)
  ./arcade.py reset      wipe progress
"""
import os, sys, json, hashlib, subprocess, secrets, string

HERE = os.path.dirname(os.path.abspath(__file__))
PROG = os.path.join(HERE, ".progress.json")
SUMS = json.load(open(os.path.join(HERE, ".checksums.json")))

LEVELS = [
    (1, "level1", "vault-lite",    "The password is sitting in the binary in plain sight. You don't even need a disassembler."),
    (2, "level2", "rolling",       "Each character is put through a per-position transform. Invert it."),
    (3, "level3", "linear system", "The check is a system of equations over the bytes. Machines are good at these."),
    (4, "level4", "keygen",        "There is no single key — the serial is computed from a name. Reproduce the algorithm."),
    (5, "level5", "anti-debug",    "The check is guarded against a debugger. Get past the guards, then read the check."),
    (6, "level6", "self-decrypt",  "The comparison runs from a page built at runtime. Catch it after it's assembled."),
    (7, "level7", "bytecode VM",   "A little virtual machine validates the key. Recover its instruction set first."),
    (8, "level8", "avalanche VM",  "Each byte feeds the next, so order matters — and it bites back if you attach."),
]

# tiered hints: concept -> tool -> region. never a value, never a key.
HINTS = {
1: ["The password is stored as a plain string inside the binary. No maths, no decode.",
    "Run: strings ./level1   (or strings -n 6 ./level1) and read the human-looking token.",
    "It's the 11-character string near the 'password:' / 'vault-lite' text. Type exactly that."],
2: ["The transform mixes your byte with its index and chains into the next comparison — so it's reversible left to right.",
    "Symbols are intact; read main. The multiply, add and the +i*i term are all visible constants.",
    "Per index i the target is ((p*A + B + i*i) & 0xff) XOR prev, prev starting at a fixed seed. Undo XOR, subtract, then multiply by the modular inverse of A mod 256 (A is odd)."],
3: ["It's linear algebra mod 256: each output equals a row of a matrix dotted with your input bytes.",
    "It's stripped — use Ghidra to find the two arrays (a 12x12 matrix and a 12-vector) and the nested loop.",
    "Feed the matrix and the target vector to z3 (pip install z3-solver) as 12 equations mod 256, one BitVec per character; solve."],
4: ["A fixed key can't exist because the launcher gives a different name each attempt; the serial is derived from that name.",
    "Stripped. Find the function that turns the name string into the serial — it runs before the string compare.",
    "It's a djb2-style rolling hash of the name (h=h*33 ^ c from a fixed seed), mixed with two constants, emitted as 16 hex nibbles grouped 4-4-4-4. Port it to Python and print the serial for any name."],
5: ["Three guards: a TracerPid read, a ptrace self-attach, and a timing check around the compare. Any one trips it.",
    "Static first (Ghidra) to read the actual check — that avoids the guards entirely. If you go dynamic, patch or skip the guards and don't single-step the timed loop.",
    "Behind the guards it's the same shape as L1/L2: target[i] = in[i] XOR K XOR (i*13). Recover K and the table statically and you never fight the anti-debug."],
6: ["The checker is copied into an RWX page (mmap) and called through a function pointer; the comparison table is XOR-encrypted in .data.",
    "Set a breakpoint on the call through the pointer, or after the copy loop, then dump the page / read the table. Ghidra shows the original checker body directly, which is the shortcut.",
    "The check is byte == (enc[i] XOR xk) for a one-byte xk. Find enc[] and xk statically and decrypt the table."],
7: ["It's a VM: a program array of opcodes driving per-lane registers. Recover what each opcode does before anything else.",
    "Stripped — in Ghidra, the dispatch is an if/else chain on the opcode byte. There are four ops and a fixed program that repeats them per character.",
    "Per lane i: acc = in[i] XOR A[i]; acc = (acc + B[i]) & 0xff; acc = rol(acc, R[i]); compare to EXP[i]. Invert: ror by R[i], subtract B[i], XOR A[i]."],
8: ["Same VM idea but each byte's result is folded into the next (prev-chained), so you must solve position 0 first and walk right. Also: it attaches to itself.",
    "The ptrace guard is one call near the top — neutralise it or work statically. The per-byte op is XOR, then multiply mod 256, then a rotate.",
    "For byte i: t = ror(EXP[i], (i%7)+1); t = t * inv(M[i]) mod 256; in[i] = t XOR A[i] XOR prev; then prev = EXP[i] for the next byte. M[i] is odd so its inverse exists."],
}

C = dict(g="\033[32m", y="\033[33m", r="\033[31m", b="\033[34m", d="\033[2m", B="\033[1m", x="\033[0m")
def col(s,c): return f"{C[c]}{s}{C['x']}" if sys.stdout.isatty() else s

def load():
    try: return set(json.load(open(PROG)).get("solved", []))
    except Exception: return set()
def save(solved):
    json.dump({"solved": sorted(solved)}, open(PROG, "w"))

def unmodified(name):
    p = os.path.join(HERE, name)
    if not os.path.exists(p): return False
    return hashlib.sha256(open(p, "rb").read()).hexdigest() == SUMS[name]

def gen_challenge():
    """Random name for the L4 keygen challenge."""
    return "USER-" + "".join(secrets.choice(string.ascii_uppercase+string.digits) for _ in range(6))

def run_check(num, name, payload, challenge=None):
    """Core verifier shared by CLI, TUI and GUI.
    Returns (ok: bool, reason: str). Never holds or reveals a key."""
    if not unmodified(name):
        return False, "that binary has been modified — restore the original to get credit."
    bpath = os.path.join(HERE, name)
    argv = [bpath] + ([challenge] if (num == 4 and challenge) else [])
    try:
        r = subprocess.run(argv, input=(payload + "\n").encode(),
                           capture_output=True, timeout=20)
    except subprocess.TimeoutExpired:
        return False, "timed out."
    return (r.returncode == 0), ("correct." if r.returncode == 0 else "nope.")

def check(num, name):
    """CLI path: prompt for the key, run the real binary, return True on success."""
    if not unmodified(name):
        print(col("  ! that binary has been modified — restore the original to get credit.", "r"))
        print(col("    (analyse a copy; patching the gate isn't a solve here)", "d"))
        return False
    if num == 4:
        chal = gen_challenge()
        print(f"  keygen target — produce the serial for this name: {col(chal,'B')}")
        ok, _ = run_check(num, name, input("  serial: ").strip(), chal)
        return ok
    ok, _ = run_check(num, name, input("  key: "))
    return ok

def hint_text(num):
    """Return (tier_index_shown, list_of_tiers) and advance the counter by one.
    Returns (None, tiers) when exhausted. Shared by CLI and GUI."""
    hp = os.path.join(HERE, f".hints_{num}")
    try: shown = int(open(hp).read().strip())
    except Exception: shown = 0
    tiers = HINTS[num]
    if shown >= len(tiers):
        return None, tiers
    open(hp, "w").write(str(shown + 1))
    return shown, tiers

def status_line(num, name, tag, solved, unlocked):
    if num in solved:  mark, cc = "✓ solved", "g"
    elif unlocked:     mark, cc = "○ open",   "y"
    else:              mark, cc = "🔒 locked", "d"
    return f"  {col(f'L{num}','B')}  {name:<8} {tag:<14} {col(mark,cc)}"

def play():
    solved = load()
    while True:
        highest_open = (max(solved)+1) if solved else 1
        print("\n" + col("═══ crackme arcade ═══", "b"))
        for num, name, tag, _ in LEVELS:
            unlocked = num <= highest_open
            print(status_line(num, name, tag, solved, unlocked))
        print(col(f"  {len(solved)}/{len(LEVELS)} solved", "d"))
        print(col("  choose a level number, 'h N' for a hint, or 'q' to quit.", "d"))
        try: sel = input("> ").strip()
        except (EOFError, KeyboardInterrupt): print(); return
        if sel in ("q","quit","exit"): return
        if sel.startswith("h"):
            parts = sel.split()
            if len(parts)==2 and parts[1].isdigit(): show_hint(int(parts[1]), solved)
            else: print("  usage: h <level number>")
            continue
        if not sel.isdigit(): continue
        num = int(sel)
        lvl = next((l for l in LEVELS if l[0]==num), None)
        if not lvl: print("  no such level."); continue
        if num > highest_open:
            print(col(f"  L{num} is locked — solve L{highest_open} first.", "d")); continue
        _, name, tag, brief = lvl
        print(f"\n{col(f'L{num} · {tag}','B')} — {brief}")
        print(col(f"  binary: {os.path.join('arcade', name)}   (analyse it, then enter the key)", "d"))
        try:
            if check(num, name):
                print(col("  ✓ correct — level cleared.", "g"))
                solved.add(num); save(solved)
                if num == len(LEVELS):
                    print(col("\n  ★ all levels cleared. you reversed the whole ladder. ★", "g"))
            else:
                print(col("  ✗ nope.", "r"))
        except (EOFError, KeyboardInterrupt):
            print()
        except subprocess.TimeoutExpired:
            print(col("  (timed out)", "r"))

def show_hint(num, solved):
    if not any(l[0]==num for l in LEVELS): print("  no such level."); return
    hp = os.path.join(HERE, f".hints_{num}")
    try: shown = int(open(hp).read().strip())
    except Exception: shown = 0
    tiers = HINTS[num]
    if shown >= len(tiers):
        print(col(f"  L{num}: no more hints — the last one is as far as I go.", "d")); return
    print(col(f"  hint {shown+1}/{len(tiers)} for L{num}:", "y"), tiers[shown])
    open(hp, "w").write(str(shown+1))

def main():
    args = sys.argv[1:]
    if not args: play()
    elif args[0] == "hint" and len(args)==2 and args[1].isdigit(): show_hint(int(args[1]), load())
    elif args[0] == "reset":
        for f in os.listdir(HERE):
            if f == ".progress.json" or f.startswith(".hints_"):
                os.remove(os.path.join(HERE, f))
        print("  progress and hint counters reset.")
    else: print(__doc__)

if __name__ == "__main__":
    main()
