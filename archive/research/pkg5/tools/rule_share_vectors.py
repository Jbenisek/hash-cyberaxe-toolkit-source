#!/usr/bin/env python3
"""tools/rule_share.c against the real compression. Research helper, not submitted.

    rule_share vectors N SEED | python3 -B tools/rule_share_vectors.py

Reads lines "nine state words, alpha, member number, z, pass" from stdin. For each line the trial is built with the
program of the package (experiments/halfsearch.py), its two real messages are compressed in full by that program's
2-round compression, and three things are compared with the C program's: z, which is ROL(Y14, 8) of message A
(Y14 = ROR(z, 8), proof.md Lemma A); rule A on the real h1; and Y4, which must be the member. Where the organizer's
reference hash is next to this folder, the digest of message A from that compression is also compared with it.
Prints one line; exit status 0 only if every vector agrees.
"""
import importlib.util
import struct
import sys
from pathlib import Path

sys.dont_write_bytecode = True
PKG = Path(__file__).resolve().parent.parent


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


hs = load("halfsearch_pkg5", PKG / "blake3-r2" / "experiments" / "halfsearch.py")
ORG = PKG.parent.parent / "hash-smash" / "verifier" / "blake3.py"
org = load("organizer_blake3", ORG) if ORG.exists() else None

n = good = passes = with_org = 0
for line in sys.stdin:
    t = line.split()
    if len(t) != 13:
        continue
    nine, alpha, k, z, p = [int(x, 16) for x in t[:9]], int(t[9], 16), int(t[10]), int(t[11], 16), int(t[12])
    X, S, w = hs.context(nine)
    y4 = hs.class_member(k)
    A, B = hs.messages(hs.trial(X, S, w, alpha, y4)[0])
    wa, da, ya = hs.compress2(A)
    ref = hs.reference(X, S, w, alpha, y4)
    ok = ya[4] == y4 and ref["y4"] == y4 and ref["half"] == 1 and hs.rol(ya[14], 8) == z and hs.rule_a(ref["h1"]) == bool(p)
    if org is not None:
        ok = ok and tuple(da) == struct.unpack("<8I", org.blake3(A, 2))
        with_org += 1
    n += 1
    good += int(ok)
    passes += p
print("VECTORS %d, z and rule A of the C program equal those of the real compression in %d; satisfy rule A %d; "
      "digest compared with the organizer's reference hash in %d" % (n, good, passes, with_org))
sys.exit(0 if n and good == n else 1)
