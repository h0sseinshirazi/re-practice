# crackme05 — authv5 (finale)

**Status:** open.

The online rung, done properly. The client verifies a signature from an activation
server on 127.0.0.1:8090.

```
cd crackme05
python3 server.py      # terminal 1
./authv5               # terminal 2
```

`server.py` and `priv.pem` are the **server side**. They're here so the rung can run, and
reading them is out of bounds.
