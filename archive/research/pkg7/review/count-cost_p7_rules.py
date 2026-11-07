#!/usr/bin/env python3
"""Reviewer (count and cost), research/pkg7 DRAFT. Three things, own code on top of count-cost_p7_tracer.py:

  1. the machine counts of the program with RULE_CONDITIONS = 4 and = 6 (the two other rows of the rule table of
     proof.md Section 10), each lane checked against the rule typed here on h1 of the real message;
  2. Lemma A (b), (c), (d) as typed here from proof.md 6.3, for all 131,072 members and random lanes with filled
     guard bits and neighbours;
  3. a sample of the share of the trials that satisfy rule A and of the batches that would run stage 2:
     CONTEXTS random contexts, all 18,725 batches each (h1 anchored against the own compression on a sub-sample).

usage: python -B count-cost_p7_rules.py CONTEXTS SEED
"""
import importlib.util
import pathlib
import random
import sys
import types

HERE = pathlib.Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location("p7tracer", HERE / "count-cost_p7_tracer.py")
T = importlib.util.module_from_spec(spec)
spec.loader.exec_module(T)
M32 = 0xFFFFFFFF


def load_rule(nc):
    src = T.PROGRAM.read_text(encoding="utf-8")
    if src.count("\nRULE_CONDITIONS = 8\n") != 1:
        raise SystemExit("RULE_CONDITIONS line not found once")
    mod = types.ModuleType("hs_rule_%d" % nc)
    mod.__file__ = str(T.PROGRAM)
    sys.modules[mod.__name__] = mod
    exec(compile(src.replace("\nRULE_CONDITIONS = 8\n", "\nRULE_CONDITIONS = %d\n" % nc), str(T.PROGRAM), "exec"), mod.__dict__)
    return mod


def rule_text(h1, nc):
    h = [(h1 >> i) & 1 for i in range(32)]
    ok = h[0] == 0 and h[1] == 1 and h[16] == 0 and h[17] == 0
    if nc >= 6:
        ok = ok and h[2] ^ h[10] == 1 and h[3] ^ h[11] == 1
    if nc >= 8:
        ok = ok and h[3] ^ h[12] ^ h[24] == 0 and h[6] ^ h[13] ^ h[25] == 0
    return ok


def counts_for(nc, cases, seed):
    hs = load_rule(nc)
    rng = random.Random(seed)
    seen, regs, right, total, passed = None, 0, 0, 0, 0
    for case in range(cases):
        free = [rng.getrandbits(32) for _ in range(7)]
        j = 18724 if case % 4 == 3 else rng.randrange(18725)
        c = hs.memory(free)
        for name in ("outer step", "table build", "middle step", "batch"):
            t = T.Trace()
            t.kept_mode = 9
            if name == "outer step":
                hs.outer_step(t, c)
            elif name == "table build":
                row = hs.table_build(t, c, j)
            elif name == "middle step":
                hs.middle_step(t, c)
            else:
                words, flags, taken, flags_a, taken_a = hs.packed_batch(t, c, row, j, case)
        cnt = t.counts()
        a = [sum(cnt[p][x] for p in T.STAGE_A) for x in range(2)]
        s2 = [sum(v[x] for v in cnt.values()) - a[x] for x in range(2)]
        now = (tuple(a), tuple(s2))
        if seen is None:
            seen = now
        elif seen != now:
            raise SystemExit("counts differ between cases")
        regs = max(regs, t.registers(True))
        v = hs.context(free)
        for i in range(7):
            y4 = T.member_text(min(7 * j + i, 131071))
            w, _ = hs.trial(v, y4)
            da, ycol, mp = T.compress2(hs.messages(w)[0])
            h1 = T.rotr(ycol[14] ^ ((ycol[3] + ycol[4] + mp[14]) & M32), 16)
            total += 1
            right += (flags_a[i] == 0) == rule_text(h1, nc)
            passed += rule_text(h1, nc)
    print("rule %d: stage A %d + %d = %d, stage 2 %d + %d = %d, registers of the batch %d; stage-A flag right in %d of %d lanes (%d satisfy the rule)"
          % (nc, seen[0][0], seen[0][1], sum(seen[0]), seen[1][0], seen[1][1], sum(seen[1]), regs, right, total, passed))


def lemma_a(seed, words):
    """(b), (c), (d) of Lemma A, typed from the text."""
    rng = random.Random(seed)
    ALL = 0x4F010300
    wrong = checked = holds = 0
    for _ in range(words):
        big = rng.getrandbits(36 * 3)                    # three lanes; the middle one is read
        z = (big >> 36) & M32
        s = (big << 12) & (0x0003C000 << 36 | 0x0003C000 | 0x0003C000 << 72); y = big ^ s
        s = s << 12; y = y ^ s
        s = (y << 13) & (0x40010000 << 36 | 0x40010000 | 0x40010000 << 72); y = y ^ s
        ylane = (y >> 36) & ((1 << 36) - 1)
        zb = [(z >> i) & 1 for i in range(32)]
        for k in rng.sample(range(131072), 2048) if words > 1 else range(131072):
            e1 = (T.member_text(k) + T.Y3) & M32
            e = [(e1 >> i) & 1 for i in range(32)]
            h1 = T.rotr(T.rotr(z, 8) ^ e1, 16)
            # (a): h[i] = z[(i+24)%32] ^ e[(i+16)%32]
            a_ok = all(((h1 >> i) & 1) == zb[(i + 24) % 32] ^ e[(i + 16) % 32] for i in range(32))
            b = (zb[24] == 0 and zb[25] == 1 and zb[8] == 1 and zb[9] == 1 and zb[26] ^ zb[2] == 0
                 and zb[27] ^ zb[3] == e[27] and zb[27] ^ zb[4] ^ zb[16] == e[28] and zb[30] ^ zb[5] ^ zb[17] == 1 ^ e[29])
            v = (1 << 24) | (1 << 26) | ((1 ^ e[27]) << 27) | ((1 ^ e[27] ^ e[28]) << 16) | (e[29] << 30)
            u = (ylane ^ v) & ALL
            cc = u == ALL
            d = ((u + (2 ** 32 - ALL)) >> 32) & 1 == 1 and u + (2 ** 32 - ALL) <= 2 ** 32 if cc else ((u + (2 ** 32 - ALL)) >> 32) == 0
            want = T.rule_a_text(h1)
            checked += 1
            holds += want
            wrong += not (a_ok and b == want and cc == want and d)
    return checked, wrong, holds


def share(hs, contexts, seed):
    rng = random.Random(seed)
    g, rol, ror = hs.g, hs.rol, hs.ror
    members = [T.member_text(k) for k in range(131072)]
    tot_t = tot_b = pas_t = pas_b = anchor = anchor_bad = 0
    per = []
    for cidx in range(contexts):
        free = [rng.getrandbits(32) for _ in range(7)]
        v = hs.context(free)
        x4w2 = v["X4"] + v["w2"]
        rx15 = rol(hs.X15, 8)
        pb = 0
        for j in range(18725):
            hit = 0
            for i in range(7 if j < 18724 else 4):
                y4 = members[7 * j + i]
                r = hs.member(v, y4)
                x0 = (r["C0.a1"] - x4w2) & M32
                x10 = (v["S10"] + (rx15 ^ x0) + hs.X15) & M32
                y14 = g(v["X2"], r["X6"], x10, v["X14"], v["w7"], v["w0"])[3]
                h1 = ror(y14 ^ ((T.Y3 + y4) & M32), 16)
                ok = T.rule_a_text(h1)
                if (7 * j + i) % 4093 == cidx:
                    w, _ = hs.trial(v, y4)
                    _, ycol, mp = T.compress2(hs.messages(w)[0])
                    anchor += 1
                    anchor_bad += h1 != T.rotr(ycol[14] ^ ((ycol[3] + ycol[4] + mp[14]) & M32), 16)
                hit |= ok
                pas_t += ok
            tot_t += 7 if j < 18724 else 4
            pb += hit
        per.append(pb / 18725)
        pas_b += pb
        tot_b += 18725
    import math
    mean = pas_b / tot_b
    sd = (sum((x - mean) ** 2 for x in per) / max(len(per) - 1, 1)) ** 0.5
    print("entry sample: %d contexts, %d trials; share of the trials that satisfy rule A 2^%.4f; share of the batches %.5f "
          "(budget 0.03125; independent trials 0.02701); single contexts %.4f to %.4f, standard deviation %.4f, "
          "standard error of the mean %.4f; h1 anchored on %d trials, wrong %d"
          % (contexts, tot_t, math.log2(pas_t / tot_t), mean, min(per), max(per), sd, sd / len(per) ** 0.5, anchor, anchor_bad))


def main():
    contexts, seed = int(sys.argv[1]), int(sys.argv[2])
    counts_for(4, 120, seed)
    counts_for(6, 120, seed + 1)
    c1 = lemma_a(seed + 2, 1)
    c2 = lemma_a(seed + 3, 600)
    print("Lemma A as typed: one lane word with all 131,072 members: checked %d, wrong %d, rule holds %d; 600 lane words with 2,048 members each: checked %d, wrong %d, rule holds %d"
          % (c1 + c2))
    sys.stdout.flush()
    if contexts:
        share(T.load_program(), contexts, seed + 4)
    return 0


if __name__ == "__main__":
    sys.exit(main())
