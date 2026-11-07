"""Roll the B3R4sel appA.py changes to a row: step size, generator calls, select count and 6-byte records, generator factor 250.
usage: python -B roll_appA.py <row dir>   (reads <row dir>/roll_nums.json)"""
import sys, os, re, json
D = sys.argv[1]
n = json.load(open(os.path.join(D, "roll_nums.json")))
P = os.path.join(D, "appA.py")
t = open(P, encoding="utf-8", newline="").read()


def sub(pat, new):
    global t
    t, k = re.subn(pat, lambda m: new, t)
    assert k == 1, pat


ph, gc, sel, body = n["ops"], 2 * n["gen_calls"], n["by"]["m"], n["body"]
sub(r"PH, STEPI, FILT, LOOP, LANES = \d+, \d+, 34, 3, 256 ", "PH, STEPI, FILT, LOOP, LANES = %d, %d, 34, 3, 256 " % (ph, ph))
sub(r"GEN_CALLS = \d+ +# generator primitive calls, both passes \(the C port; 2 x [\d,]+ in python3 bsrho.py --ledger\)\n",
    "GEN_CALLS = %d                              # generator primitive calls, both passes (the C port; 2 x %s in python3 bsrho.py --ledger)\n"
    "NSEL, SEL = %d, 6                            # select gates of the step (of the %s), bytes per select record\n" % (gc, format(gc // 2, ","), sel, format(ph, ",")))
sub(r"HIT, EVENT, CUTOPS, SLICE, GEN_FACTOR = 2800, 3800, 4200, 1300, 200\n", "HIT, EVENT, CUTOPS, SLICE, GEN_FACTOR = 2800, 3800, 4200, 1300, 250\n")
sub(r"# one batch = [\d,]+ operations", "# one batch = %s operations" % format(body, ","))
sub(r"code_bytes = \(STEPI \+ FILT \+ PH7\) \* GATE \+ \(LOOP \+ OTHER_CODE\) \* INSTR +# gates of the step, the stage-1 test and the recovery circuit at 5 bytes",
    "code_bytes = (STEPI + FILT + PH7) * GATE + NSEL * (SEL - GATE) + (LOOP + OTHER_CODE) * INSTR     # gates of the step, the stage-1 test and the recovery circuit at 5 bytes, select gates at 6")
sub(r'rows = \[\("main loop: B \* \d+", body \* B\),', 'rows = [("main loop: B * %d" % body, body * B),')
open(P, "w", encoding="utf-8", newline="").write(t)
print("patched", P)
