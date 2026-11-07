#!/usr/bin/env python3
"""wdiff_profile.py - SHA-256 message-schedule difference profiler.

Usage:
    wdiff_profile.py PAIRFILE R [PAIRFILE R ...] [--xml CHAR.xml]

For each PAIRFILE it reads the 'M1'/'M2' lines (16 hex words each), expands
both messages to R words using the SHA-256 message schedule, and prints the
signed-difference profile row by row plus a footer summary.

With --xml CHAR.xml it prints the same style of profile taken directly from
the 'W:' columns of a characteristic xml (only u/n signs are kept).
"""
import sys

MASK = 0xFFFFFFFF


def rotr(x, n):
    return ((x >> n) | (x << (32 - n))) & MASK


def sigma0(x):
    return rotr(x, 7) ^ rotr(x, 18) ^ (x >> 3)


def sigma1(x):
    return rotr(x, 17) ^ rotr(x, 19) ^ (x >> 10)


def expand(words, R):
    W = list(words[:16])
    for t in range(16, R):
        v = (sigma1(W[t - 2]) + W[t - 7] + sigma0(W[t - 15]) + W[t - 16]) & MASK
        W.append(v)
    return W[:R]


def sign_from_words(a, b):
    s = []
    for i in range(31, -1, -1):
        ba = (a >> i) & 1
        bb = (b >> i) & 1
        if ba == bb:
            s.append('-')
        elif ba == 1:
            s.append('u')
        else:
            s.append('n')
    return ''.join(s)


def moddiff_from_sign(sign):
    val = 0
    for idx, ch in enumerate(sign):
        pos = 31 - idx
        if ch == 'u':
            val += (1 << pos)
        elif ch == 'n':
            val -= (1 << pos)
    d = val & MASK
    if d >= (1 << 31):
        d -= (1 << 32)
    return d


def hexsigned(v):
    return ("-0x%x" % (-v)) if v < 0 else ("0x%x" % v)


def print_profile(label, signs):
    R = len(signs)
    print("== %s (R=%d) ==" % (label, R))
    diff_rows = []
    total = 0
    lo = 0
    hi = 0
    for t, sg in enumerate(signs):
        ham = sum(1 for c in sg if c != '-')
        if ham == 0:
            continue
        diff_rows.append(t)
        total += ham
        if t < 16:
            lo += ham
        else:
            hi += ham
        md = moddiff_from_sign(sg)
        print("%3d  %s  hw=%2d  dmod=%s" % (t, sg, ham, hexsigned(md)))
    last = diff_rows[-1] if diff_rows else -1
    free = (R - 1 - last) if last >= 0 else R
    print("-- footer --")
    print("diff rows: %s" % (" ".join(str(x) for x in diff_rows) if diff_rows else "(none)"))
    print("last diff row: %d" % last)
    print("free rows = R-1-lastdiff = %d" % free)
    print("total active bits: %d" % total)
    print("active bits rows<16: %d  rows>=16: %d" % (lo, hi))
    print("")


def read_pair(path):
    m1 = m2 = None
    with open(path) as f:
        for line in f:
            tok = line.split()
            if not tok:
                continue
            if tok[0] == 'M1' and len(tok) >= 17:
                m1 = [int(x, 16) & MASK for x in tok[1:17]]
            elif tok[0] == 'M2' and len(tok) >= 17:
                m2 = [int(x, 16) & MASK for x in tok[1:17]]
    if m1 is None or m2 is None:
        raise SystemExit("error: %s missing M1/M2 lines" % path)
    return m1, m2


def do_pair(path, R):
    m1, m2 = read_pair(path)
    W1 = expand(m1, R)
    W2 = expand(m2, R)
    signs = [sign_from_words(W1[t], W2[t]) for t in range(R)]
    print_profile(path, signs)


def read_xml_signs(path):
    signs = []
    with open(path) as f:
        for line in f:
            if 'W:' not in line:
                continue
            after = line.split('W:', 1)[1]
            best = None
            for tok in after.replace('"', ' ').replace('<', ' ').replace('>', ' ').split():
                if tok and all(c in '-un01x?nu' for c in tok) and len(tok) >= 32:
                    cand = tok[:32]
                    if any(c in 'un' for c in cand) or best is None:
                        best = cand
            if best is None:
                # fall back: grab first 32-char condition token even if all '-'
                for tok in after.split():
                    if len(tok) >= 32:
                        best = tok[:32]
                        break
            if best is not None:
                # keep only u/n, everything else becomes '-'
                sg = ''.join(c if c in 'un' else '-' for c in best)
                signs.append(sg)
    return signs


def do_xml(path):
    signs = read_xml_signs(path)
    print_profile(path + " [xml]", signs)


def main(argv):
    if len(argv) < 2:
        raise SystemExit(__doc__)
    i = 1
    while i < len(argv):
        a = argv[i]
        if a == '--xml':
            if i + 1 >= len(argv):
                raise SystemExit("error: --xml needs a file")
            do_xml(argv[i + 1])
            i += 2
        else:
            if i + 1 >= len(argv):
                raise SystemExit("error: PAIRFILE needs an R value")
            R = int(argv[i + 1])
            do_pair(a, R)
            i += 2


if __name__ == '__main__':
    main(sys.argv)
