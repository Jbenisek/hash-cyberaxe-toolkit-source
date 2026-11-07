#!/usr/bin/env python3
"""condcount.py - condition counter for SHA-2 differential characteristic XML."""
import sys
import re
import xml.etree.ElementTree as ET

UN = set('un')          # signed difference bits
FIX = set('01')         # fixed value bits
DIFF = set('xun')       # any difference marker (for W window / pair check)


def parse_char(path):
    # text parse (ElementTree normalises the newlines inside the char attribute to spaces) - Lattice 10-30
    txt = open(path, encoding='utf-8').read()
    mn = re.search(r'name="n"\s+value="(\d+)"', txt); n = int(mn.group(1)) if mn else None
    i = txt.index('<char value="') + len('<char value="'); j = txt.index('"/>', i)
    char = txt[i:j]
    rows = []
    rx = re.compile(r'\s*(-?\d+)\s+A:\s*(\S+)\s+E:\s*(\S+)(?:\s+W:\s*(\S+))?')
    for line in char.splitlines():
        if not line.strip():
            continue
        m = rx.match(line)
        if not m:
            continue
        idx = int(m.group(1))
        A, E, W = m.group(2), m.group(3), m.group(4)
        rows.append((idx, A, E, W))
    return n, rows


def cnt(s, charset):
    if not s:
        return 0
    return sum(1 for c in s if c in charset)


def load_pair(path, n):
    toks = open(path).read().split()
    vals = []
    for t in toks:
        t = t.lower()
        if t.startswith('0x'):
            t = t[2:]
        try:
            vals.append(int(t, 16))
        except ValueError:
            pass
    if len(vals) < 2 * n:
        sys.exit("pair file: expected 2*%d hex words, got %d" % (n, len(vals)))
    return vals[:n], vals[n:2 * n]


def main():
    args = sys.argv[1:]
    pairfile = None
    files = []
    i = 0
    while i < len(args):
        if args[i] == '--pair':
            pairfile = args[i + 1]
            i += 2
        else:
            files.append(args[i])
            i += 1
    if len(files) != 1:
        sys.exit("usage: condcount.py CHAR.xml [--pair PAIRFILE]")

    n, rows = parse_char(files[0])

    print("%4s %4s %4s %4s %4s %5s %6s" %
          ("row", "unA", "unE", "unW", "fix", "cond", "cum"))
    cum = 0
    data = []
    wdiff_idxs = []
    for idx, A, E, W in rows:
        unA = cnt(A, UN)
        unE = cnt(E, UN)
        unW = cnt(W, UN)
        fix = cnt(A, FIX) + cnt(E, FIX)
        cond = unA + unE + fix
        cum += cond
        data.append((idx, unA, unE, unW, fix, cond))
        if W and cnt(W, DIFF) > 0:
            wdiff_idxs.append(idx)
        print("%4d %4d %4d %4d %4d %5d %6d" %
              (idx, unA, unE, unW, fix, cond, cum))

    print()
    print("=== footer ===")
    if wdiff_idxs:
        first_w, last_w = wdiff_idxs[0], wdiff_idxs[-1]
        before = sum(d[5] for d in data if d[0] < first_w)
        window = sum(d[5] for d in data if first_w <= d[0] <= last_w)
        after = sum(d[5] for d in data if d[0] > last_w)
        print("first W diff row: %d   last W diff row: %d" % (first_w, last_w))
        print("window conditions  before [row<%d]      : %d" % (first_w, before))
        print("window conditions  [%d .. %d]           : %d" % (first_w, last_w, window))
        print("window conditions  after  [row>%d]      : %d" % (last_w, after))
    else:
        print("no W difference columns found")

    print("densest 5 rows (by cond):")
    for d in sorted(data, key=lambda x: (-x[5], x[0]))[:5]:
        print("   row %4d  cond=%d" % (d[0], d[5]))

    total_conditions = sum(d[5] for d in data)
    print("total conditions (u/n + 0/1 over A and E, W excluded): %d" % total_conditions)

    if pairfile:
        print()
        print("=== pair verification ===")
        m1, m2 = load_pair(pairfile, n)
        ok = True
        for idx, A, E, W in rows:
            if W is None or idx < 0 or idx >= n:
                continue
            diff = m1[idx] ^ m2[idx]
            mism = []
            for p, c in enumerate(W):
                bit = (diff >> (31 - p)) & 1
                if c in DIFF and bit != 1:
                    mism.append(p)
                elif c in '-01' and bit != 0:
                    mism.append(p)
                # '?' : unconstrained
            status = "MATCH" if not mism else "MISMATCH@" + ",".join(map(str, mism))
            if mism:
                ok = False
            print("W row %4d : %s" % (idx, status))
        print("overall: %s" % ("MATCH" if ok else "MISMATCH"))


if __name__ == '__main__':
    main()
