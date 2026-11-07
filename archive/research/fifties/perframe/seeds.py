#!/usr/bin/env python3
"""seeds.py - generator keys of the perframe run. python3 -B seeds.py <kind> -> 'keyhexG1 keyhexG2'.
keyhex(kind, g) = sha256(SEED_TEXT % (kind, g)).hexdigest(); G1 uses its first 8 bytes as the Philox4x32-10 key (two
big-endian words), G2 uses all 32 bytes as the SHA-256 message prefix."""
import hashlib
import sys

SEED_TEXT = ("HashSmash perframe 9a9f3b7b H7prime-ak-cluster per-frame clustering of deep trial events, frame search "
             "of proof.md 9, counter instance, 2026-10-09 | %s | G%d")


def keyhex(kind, g):
    return hashlib.sha256((SEED_TEXT % (kind, g)).encode()).hexdigest()


if __name__ == "__main__":
    print(keyhex(sys.argv[1], 1), keyhex(sys.argv[1], 2))
