"""Check a block pair written by kpipe (freestart mode) against the organizer reference compression.

Usage: python3 verify_pair.py <pair.txt>
The file gives flags, counter, block_len, cv (8 words), mA and mB (16 words each).
Runs hash-smash/verifier/blake3.py:_compress with rounds=2 on both blocks and compares all 16 output words.
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REF = os.path.normpath(os.path.join(HERE, "..", "..", "..", "..", "hash-smash"))
sys.path.insert(0, REF)
from verifier import blake3 as ref  # noqa: E402


def main(path):
    vals = {}
    with open(path) as f:
        for line in f:
            parts = line.split()
            if parts:
                vals[parts[0]] = parts[1:]
    flags = int(vals["flags"][0])
    counter = int(vals["counter"][0])
    blen = int(vals["block_len"][0])
    cv = tuple(int(w, 16) for w in vals["cv"])
    ma = tuple(int(w, 16) for w in vals["mA"])
    mb = tuple(int(w, 16) for w in vals["mB"])
    oa = ref._compress(cv, ma, counter, blen, flags, 2)
    ob = ref._compress(cv, mb, counter, blen, flags, 2)
    diff = [i for i in range(16) if ma[i] != mb[i]]
    print("reference:", ref.__file__)
    print("cv =", " ".join("%08x" % w for w in cv))
    print("message words that differ:", ["m%d" % i for i in diff])
    print("out A =", " ".join("%08x" % w for w in oa))
    print("out B =", " ".join("%08x" % w for w in ob))
    print("cv-output (first 8 words) equal:", oa[:8] == ob[:8], "| all 16 output words equal:", oa == ob)
    print("cv is the standard IV:", cv == tuple(ref.IV))


if __name__ == "__main__":
    main(sys.argv[1])
