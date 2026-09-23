# crackme05 — authv5 (finale)

**Solver:** [`solvers/patch_authv5.py`](solvers/patch_authv5.py) (writes `crackme05/authv5.patched`)

## Protocol

1. Connect to 127.0.0.1:8090 and read a 32-byte nonce (as hex).
2. Send `AUTH <key>`.
3. Read the reply. If it starts with `DENY`, the key is refused (`strncmp …, 4` @ 0x150f).
4. Otherwise hex-decode it as a signature, and verify it over the nonce with the **Ed25519 public
   key** embedded at `.rodata 0x20e0` (`EVP_PKEY_new_raw_public_key(0x43f = ED25519)`,
   `EVP_DigestVerify` @ 0x1612).

## Why every "external" attack fails

| Attack | Result |
|---|---|
| Recover a secret from the client | It only holds a public key, which verifies but can't sign. |
| Replay a captured signature | Every run has a fresh nonce, so an old signature doesn't match. |
| Fake the server (the authme trick) | You'd need to sign the nonce, which needs the private key. |
| Keygen | No validation algorithm exists client-side to copy. |

## The route that's left: change the client

The crypto is sound. The **decision** is still just instructions on a machine you control:

```asm
1518  je    0x15e6            ; reply was "DENY" → "activation refused"
162a  cmp   r14d, 1           ; EVP_DigestVerify == 1 ?
163c  cmove rdi, rax          ; pick "*** ACTIVATED ***" only if so
```

Two patches:

| Offset | Original | Patched | Effect |
|---|---|---|---|
| 0x1518 | `0f 84 c8 00 00 00` (`je`) | `90 ×6` | don't bail on DENY |
| 0x163c | `48 0f 44 f8` (`cmove rdi, rax`) | `48 89 c7 90` (`mov rdi, rax`) | always pick ACTIVATED |

With the server running, `./authv5.patched` activates with any key. It still needs
*something* listening on 8090, because the connect happens before either patch site.

**Another patch** that feels more "legitimate": overwrite the 32-byte public key at
0x20e0 with one of your own, then run your own server that signs nonces with the matching
private key. The protocol runs end to end, just against a root of trust you replaced.

## Takeaway

Cryptography protects messages, but it doesn't protect the program that checks them. When the
verifier runs on the attacker's machine, it's a branch the attacker can edit. That's why real
licensing moves value to the server (features and content it only serves to valid accounts)
instead of trying to prove activation to the client.
