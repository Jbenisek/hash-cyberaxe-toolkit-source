import json, os
OUT = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
EV = "research/dig/incoming2/sha256-38-G04-U02/work/ (cv38.c, run.sh; val.out dep.out dcv.out f7.out bij.out cnt.out real.out)"
VAL = ("Validated first on the published chi38 pair: both members digests equal the published digest, rows -4..6 A/E equal, Step-2 map reproduces published W0..W7 (x and y), dW16 = 0xe0000000, published W16 in G, "
       "|F7| recount over all 2^32 = 287,309,824 (matches proof), fast W16 vs generic Step-2 on 2e5 random CV: 0 mismatches. Scope: the published dense part A0..A7 and published W9, W14 (a window: one variant, not the 256 x R_j family); "
       "W16 recomputed from W0..W15, no held-fixed expanded word.")
W = {
 'A-3': dict(name='A_-3', lab='CV word A_-3 (c of the state before step 0)', ri=-3, partner='W5', dep='W0..W5 (not W6, W7)'),
 'A-4': dict(name='A_-4', lab='CV word A_-4 (d of the state before step 0)', ri=-4, partner='W4', dep='W1..W4 (not W0, not W5..W7)'),
 'E-4': dict(name='E_-4', lab='CV word E_-4 (h of the state before step 0)', ri=-4, partner='W0', dep='W0 only'),
}
BIJ = "Step-2 map CV -> W0..W7 for the published dense part: %s = C - %s exactly (partner(x)+x constant) on 1,073,741,824 of 1,073,741,824 samples (64 random other-7-word settings x 2^24 values), so the word is a bijective image of %s"
DEP = "exact-sensitivity matrix over 20000 random CV (redraw one word): the word changes %s; zero change elsewhere"
CNTTXT = {
 'A-3': "exhaustive over all 2^32 values of A_-3, W16 in G (the 32-word row-16 set, 0x35f29010 + subset of bits 0,2,10,13,19): published CV 65,536 values (2^16), 6 random CV settings 0,0,0,0,0,0 (mean 0.000); A_-3 reaches W16 only through MAJ(A_-1,A_-2,A_-3) (the +A_-3 in E1 cancels in W1), so W16 takes only 2^popcount(A_-1 xor A_-2) distinct values over A_-3 (popcount 16, 12, 15, 15, 20, 16, 22 in the 7 settings) and a hit is a lump of 2^(32-pc) values (published: 2^16)",
 'A-4': "exhaustive over all 2^32 values of A_-4, W16 in G: published CV 41; 6 random CV settings 38, 23, 46, 30, 28, 26 (mean 31.83, min 23, max 46; every setting at least 1 hit; a plain bijection onto W16 would give mean 32)",
 'E-4': "exhaustive over all 2^32 values of E_-4, W16 in G: exactly 32 in each of the 7 settings (published CV + 6 random), as W16 = const - E_-4 in this window",
}
CNTNUM = {'A-3': 'published CV 65,536 = 2^16, random 0,0,0,0,0,0',
          'A-4': 'published 41, random 38,23,46,30,28,26',
          'E-4': '32 exactly in 7 of 7 settings'}
REALTXT = {
 'A-3': "A_-3: top-byte chi2 257.4 (255 dof, p 0.447), low-byte 243.7 (p 0.683), given W7 in F7 270.2 (p 0.245), given F7 and top 10 bits of W16 equal to the G prefix 215.9 (p 0.964); max |z| over 32 bits 2.23 (2.20 given F7)",
 'A-4': "A_-4: top-byte chi2 225.4 (p 0.909), low-byte 256.7 (p 0.458), given F7 277.2 (p 0.163), given F7 + W16 prefix 243.5 (p 0.687); max |z| 2.35 (2.83 given F7)",
 'E-4': "E_-4: top-byte chi2 281.8 (p 0.120), low-byte 240.0 (p 0.742), given F7 231.5 (p 0.852), given F7 + W16 prefix 273.9 (p 0.198); max |z| 1.98 (2.52 given F7)",
}
REALHEAD = ("2^30 (1,073,741,823) random first blocks M0, CV1 = F38(IV, M0) with feed-forward (seed 3802): W7 in F7 gate 71,830,206 = 0.066897 (|F7|/2^32 = 0.066895); "
            "F7 and top-10 bits of W16 in G prefix 70,147 (expected 70,146.7). ")
DCV = {
 'A-3': "A_-3 + 1 in member y with the same message: state rows 0..37 differ in 37 rows and all 8 digest words differ",
 'A-4': "A_-4 + 1 in member y with the same message: state rows 0..37 differ in 38 rows and all 8 digest words differ",
 'E-4': "E_-4 + 1 in member y with W0 reduced by 1 (the only word E_-4 reaches in rows 0..15): rows 0..15 identical, rows 16..37 differ (22 rows, through W16 = ... + W0), all 8 digest words differ",
}
recs = []
def add(k, q, status, number, question, notes, labels):
    w = W[k]; cell = "sha256-38|CV.%s|CV|%s" % (k, q)
    recs.append((cell, dict(hash='sha256-38', row_i=w['ri'], row_j=0, source='our workflow: scan-once-wave2', own_test=True, date='2026-10-12',
        lever=False, gain_bits=0.0, object=w['lab'] + ' of the ordinary collision', question=question, labels=labels, status=status, number=number,
        notes=notes + ' universe cell ' + cell + '. ' + VAL, evidence=EV, gain_basis='count',
        topic='sha256-38 CV.%s ordinary collision %s' % (k, q))))
for k, w in W.items():
    n = w['name']; p = w['partner']
    bij = BIJ % (p, n, p)
    depn = DEP % w['dep']
    add(k, 'Q1', 'LOCAL_ONLY',
        "2^32 values, bijective with %s (%s = C - %s exact on 1,073,741,824/1,073,741,824 samples); feeds %s; W16-in-G count: %s" % (p, p, n, w['dep'], CNTNUM[k]),
        "Q1 count: how many values does %s take as the ordinary collision uses it, and what does it feed?" % n,
        "Count. %s. %s. Exhaustive count: %s." % (bij, depn, CNTTXT[k]),
        ['D', 'C'] if k != 'E-4' else ['D', 'I'])
    add(k, 'Q2', 'LOCAL_ONLY',
        "no gate or cell on %s (necessary-condition count 0); dCV = 0 required by digest algebra; fixing it to a constant fixes %s" % (n, p),
        "Q2 necessity: is a condition on %s needed; what happens if it is dropped, replaced by a constant, or differs between the members?" % n,
        "Necessity. No row condition or cell touches %s: its only effect is through %s and the words in the dependency matrix (%s). The event A(CV1, v) (W16 in G, W7 in F7, rows 17..37) is a function of W0..W7, so dropping a condition on %s costs nothing and gives nothing. Replacing %s by a constant is not a free move: it fixes %s, so one fresh first block carries it with probability 2^-32. %s. Real first blocks: %s%s; nothing is gated on %s. Equal-value requirement: with rows 34..37 equal in both members, digest = CV + final state, so any nonzero dCV word shows in the digest word unchanged and dCV = 0 is necessary (algebra); measured: %s."
        % (n, p, w['dep'], n, n, p, depn, REALHEAD, REALTXT[k], n, DCV[k]),
        ['D', 'N'] if k != 'E-4' else ['D', 'N', 'I'])
    add(k, 'Q3', 'LOCAL_ONLY',
        {'A-3': "log2 freedom 32 (bijective with W5); given row 16: 0 or 2^16 values per setting (published CV 65,536; 0 in 6 of 6 random settings)",
         'A-4': "log2 freedom 32 (bijective with W4); given row 16 (W16 in G): 41 at published CV, mean 31.83 over 6 random settings (min 23, max 46), about 2^5.0",
         'E-4': "log2 freedom 32 (bijective with W0); given row 16 (W16 in G): exactly 32 = 2^5 in 7 of 7 settings"}[k],
        "Q3 freedom: log2 of the values %s can take given the earlier rows and the gates?" % n,
        "Freedom. Unconditioned 2^32 (bijection onto %s, sampled identity above). Conditioned on W16 in G with the other 7 CV words fixed: %s. Uniformity on real first blocks (H1, this word): %s%s. W7 in F7 does not depend on %s (zero column of the dependency matrix)."
        % (p, CNTTXT[k], REALHEAD, REALTXT[k], n),
        ['D', 'N'] if k != 'A-3' else ['D', 'C', 'N'])
    add(k, 'Q4', 'LOCAL_ONLY',
        {'A-3': "same-W16 alternatives: 2^(32-pc) values per MAJ class (2^16 at published CV), but each gives a different W5; nonzero dCV breaks the digest",
         'A-4': "23..46 alternative A_-4 values per setting give W16 in G (mean 31.83); nonzero dCV breaks the digest",
         'E-4': "32 alternative E_-4 values per setting give W16 in G; nonzero dCV compensated by W0 keeps rows 0..15 but moves rows 16..37 and breaks the digest"}[k],
        "Q4 alternatives: other values or signings of %s that give the same event?" % n,
        "Alternatives. Same-event values: %s. Alternative signing (nonzero chaining-value difference): tested the simplest one: %s. This closes the cheap versions; a characteristic built for a nonzero dCV (second block absorbs it) is not tested here and would be a different characteristic. First blocks per value of %s: 2^512 / 2^32 = 2^480."
        % (CNTTXT[k], DCV[k], n),
        ['D', 'B'] if k != 'E-4' else ['D', 'B', 'I'])
for cell, r in recs:
    fn = cell.replace('|', '_') + '.json'
    json.dump(r, open(os.path.join(OUT, fn), 'w', encoding='utf-8'), indent=1, ensure_ascii=False)
print(len(recs))
