# crackme05 — authv5 (finale)

**Status:** open. These notes cover the design, not a solution.

`server.py` and `priv.pem` are the **server side**. They're here so the rung can run, and
reading them is out of bounds. Start the server with `python3 server.py` from this
directory, then run `./authv5`.

## What's different from authme

The client imports `EVP_PKEY_new_raw_public_key` and `EVP_DigestVerify`, which means it
verifies an **Ed25519 signature**. The protocol on 127.0.0.1:8090:

1. The server sends a fresh random 32-byte nonce.
2. The client sends `AUTH <key>`.
3. If the key is valid, the server returns a signature over *that* nonce.
4. The client checks the signature against a public key built into the binary.

## Why the authme attacks fail here

| Attack | Why it fails |
|---|---|
| Recover a secret from the client | The client only has a *public* key, which can verify but not sign. |
| Replay a captured reply | Each signature covers a new nonce, so an old one won't verify. |
| Fake the server | Producing a valid signature needs the private key, which the client never has. |
| Keygen | Validity is decided server-side, and the client has no algorithm to copy. |

The one route left is changing what the client *does* with a failed check. That's a
lesson about where trust sits: the cryptography can be sound and still lose to a user
who controls the machine it runs on.
