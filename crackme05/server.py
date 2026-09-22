#!/usr/bin/env python3
import socket, secrets, subprocess, tempfile, os
VALID = {"HOSS-V5-VALID-LICENSE"}      # server-side secret set
def sign(nonce: bytes) -> bytes:
    with tempfile.NamedTemporaryFile(delete=False) as f: f.write(nonce); msg=f.name
    sig = subprocess.run(["openssl","pkeyutl","-sign","-inkey","priv.pem",
                          "-rawin","-in",msg], capture_output=True).stdout
    os.unlink(msg); return sig
srv=socket.socket(); srv.setsockopt(socket.SOL_SOCKET,socket.SO_REUSEADDR,1)
srv.bind(("127.0.0.1",8090)); srv.listen(5)
print("activation server on 127.0.0.1:8090")
while True:
    c,_=srv.accept()
    nonce=secrets.token_bytes(32)
    c.sendall(nonce.hex().encode()+b"\n")
    data=c.recv(256).decode(errors="replace").strip()
    key=data[5:] if data.startswith("AUTH ") else ""
    if key in VALID:
        c.sendall(sign(nonce).hex().encode()+b"\n")
    else:
        c.sendall(b"DENY\n")
    c.close()
