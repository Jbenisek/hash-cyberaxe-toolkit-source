"""Stage 2: Appendix A constants.  usage: python3 -B mkroll8_appA.py R PH PH7 OTHER_CODE   (from `bsrho.py --ledger`: PH, recovery circuit operations, other code instructions)"""
import sys, os
R = int(sys.argv[1]); PH = int(sys.argv[2]); PH7 = int(sys.argv[3]); OC = int(sys.argv[4]); U = 14 + 208 * R
D = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "blake3_r%d" % R, "b8r%d" % R))
p = os.path.join(D, "appA.py"); t = open(p, encoding="utf-8", newline="").read()
def rep(a, b):
    global t
    assert t.count(a) == 1, (a, t.count(a)); t = t.replace(a, b)
rep("PH, STEPI, FILT, LOOP, LANES = 55210,", "PH, STEPI, FILT, LOOP, LANES = %d," % PH)
rep("PH7, EXTRA, PASSES = 1532,", "PH7, EXTRA, PASSES = %d," % PH7)
rep("INSTR, OTHER_CODE, REGFILE, COUNTERS, ENTRY, ADVICE, SPARE = 36, 2739,", "INSTR, OTHER_CODE, REGFILE, COUNTERS, ENTRY, ADVICE, SPARE = 36, %d," % OC)
rep("# one batch = 55,247 operations", "# one batch = {:,} operations".format(PH + 37))
rep('("main loop: B * 55247", body * B)', '("main loop: B * %d", body * B)' % (PH + 37))
rep('("recovery: 2 * (c + 2^48) * (1532 + 64) + 600"', '("recovery: 2 * (c + 2^48) * (%d + 64) + 600"' % PH7)
rep("P, C = 100000, 1470", "P, C = 100000, %d" % U)
open(p, "w", encoding="utf-8", newline="").write(t)
print("ok")
