#!/usr/bin/env python3
# Activation server for authme.
# Reconstructed 2026-09-24: the original was lost when its file was overwritten.
# Rebuilt from the client's behaviour: it connects to 127.0.0.1:8085, sends
# "AUTH <key>\n", and prints ACTIVATED only if the reply equals its grant token.
# SERVER-SIDE FILE: reading it spoils the rung.
import socket
VALID = {"HOSS-V4-VALID-LICENSE"}
GRANT = "GR4NT-R4X53GC1XM"
srv = socket.socket(); srv.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
srv.bind(("127.0.0.1", 8085)); srv.listen(5)
print("activation server on 127.0.0.1:8085")
while True:
    c, _ = srv.accept()
    data = c.recv(256).decode(errors="replace").strip()
    key = data[5:] if data.startswith("AUTH ") else ""
    c.sendall((GRANT if key in VALID else "DENY").encode() + b"\n")
    c.close()
