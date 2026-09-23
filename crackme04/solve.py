#!/usr/bin/env python3
"""authme: recover the grant token, then play the server yourself."""
import socket, sys
BLOB = bytes.fromhex("1702641e047d0264086563171361081d")  # .rodata 0x20b0
token = bytes(b ^ 0x50 for b in BLOB).decode()
print("grant token:", token)

if "--serve" in sys.argv:  # fake server: grants ANY key
    s = socket.socket(); s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    s.bind(("127.0.0.1", 8085)); s.listen(1)
    print("fake server on 127.0.0.1:8085 — run ./authme with any key")
    c, _ = s.accept(); c.recv(256); c.sendall(token.encode() + b"\n"); c.close()
