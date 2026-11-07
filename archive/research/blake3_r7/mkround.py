"""Retarget the finished r7 build folder (research/blake3_r7/b7) to another round count R (5 or 6).
usage: python -B mkround.py R          -> creates research/blake3_rR/bR (does not touch r7)
Stage 1 substitutes ROUNDS/UNIT, imports the program and reads ops, nodes, code, PH7, other code, generator calls, max use;
stage 2 substitutes every round-specific number and phrase.  Residual hits are listed for hand reading."""
import sys, os, re, shutil, subprocess, importlib
R = int(sys.argv[1]); U = 14 + 208 * R
W = {5: "five", 6: "six"}[R]
HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(HERE, "b7")
DST = os.path.join(HERE, "..", "blake3_r%d" % R, "b%d" % R)
DST = os.path.abspath(DST)
if os.path.exists(os.path.join(DST, "pkg")):
    shutil.rmtree(os.path.join(DST, "pkg"))
os.makedirs(DST, exist_ok=True)
keep = ["appA.py", "build_all.py", "proof_t.md", "note_t.md", "org_summary.py", "embed_gen.py", "bld.sh", "exp_run.sh", "tm_run.sh", "st_run.sh", "rc_run.sh", "stage_run.sh", "intake_pre.sh", "stage_pre.sh"]
for f in keep:
    shutil.copy(os.path.join(SRC, f), DST)
shutil.copytree(os.path.join(SRC, "gen_c"), os.path.join(DST, "gen_c"), dirs_exist_ok=True,
                ignore=shutil.ignore_patterns("native", "__pycache__", "gen.wasm", "cport.json", "ref_*"))
os.makedirs(os.path.join(DST, "gen_c", "native"), exist_ok=True)
for f in ("gen_native.c", "check.py"):
    shutil.copy(os.path.join(SRC, "gen_c", "native", f), os.path.join(DST, "gen_c", "native"))
shutil.copytree(os.path.join(SRC, "ext"), os.path.join(DST, "ext"), dirs_exist_ok=True, ignore=shutil.ignore_patterns("*.out", "pygen_rss.json", "__pycache__"))
shutil.copy(os.path.join(SRC, "ext", "pygen_rss.json"), os.path.join(DST, "ext"))
X = os.path.join(DST, "pkg", "blake3", "experiments")
os.makedirs(X, exist_ok=True)
os.makedirs(os.path.join(DST, "pkg", "blake3", "certificates"), exist_ok=True)
shutil.copy(os.path.join(SRC, "pkg", "blake3", "certificates", "manifest.json"), os.path.join(DST, "pkg", "blake3", "certificates"))
shutil.copy(os.path.join(SRC, "pkg", "blake3", "experiments", "manifest.json"), X)
s = open(os.path.join(SRC, "pkg", "blake3", "experiments", "bsrho.py"), encoding="utf-8", newline="").read()
s1 = s.replace("ROUNDS = 7 ", "ROUNDS = %d " % R).replace("UNIT = 1470 ", "UNIT = %d " % U)
open(os.path.join(X, "bsrho.py"), "w", encoding="utf-8", newline="").write(s1)
sys.dont_write_bytecode = True
sys.path.insert(0, X)
import bsrho as b
st = b.step256()
g = b.trace(256)[0]
import collections
cnt = collections.Counter()
for nd in g.nodes:
    if len(nd) == 3:
        cnt[nd[1]] += 1; cnt[nd[2]] += 1
maxuse = max(cnt.values())
ph7 = b.packed_circuit(st.qwords)[1]
oc = b.other_code(st)
ph, filt, body, code, _ = b.machine_constants(st)
nodes = len(g.nodes)
static = code + 16384 + (nodes + 1) + 2400 + 2048 + 68
info = dict(R=R, U=U, ops=st.ops, nodes=nodes, code=code, ph7=ph7, other=oc, gen_calls=st.gen_calls, maxuse=maxuse, static=static, body=body)
print(info)
open(os.path.join(DST, "info.txt"), "w").write(repr(info))


def fmt(n): return "{:,}".format(n)


R7 = dict(ops=45974, nodes=46231, code=1755288, ph7=1540, other=2747, gen_calls=92876, maxuse=19, pages=29)
# memory budget etc. are filled in by a second call (fix_mem) once opt.py has run; here only round-dependent facts.
reps = [
    ("ROUNDS = 7 ", "ROUNDS = %d " % R), ("blake3-r7", "blake3-r%d" % R), ("C(r7)", "C(r%d)" % R), ("blake3(M(x), 7)", "blake3(M(x), %d)" % R), ("blake3(M, 7)", "blake3(M, %d)" % R), ("blake3(M,7)", "blake3(M,%d)" % R),
    ("--rounds 7", "--rounds %d" % R), ("7-round", "%d-round" % R), ("7 rounds with", "%d rounds with" % R), ("7 rounds, unkeyed", "%d rounds, unkeyed" % R),
    ("(7 for the target)", "(%d for the target)" % R), ("#define ROUNDS 7", "#define ROUNDS %d" % R),
    ("chained for 7 steps", "chained for %d steps" % R), ("7 chained steps", "%d chained steps" % R), ("chained 7 steps", "chained %d steps" % R),
    ("for _ in range(7):", "for _ in range(%d):" % R),
    ("the full seven rounds of BLAKE3", "%s rounds" % W), ("seven rounds, the full round count", "%s rounds" % W),
    ("(222, 430, 638, 846, 1,054, 1,262 and 1,470 for 1 to 7 rounds, that is 14 + 208 r;", "(%s for 1 to %d rounds, that is 14 + 208 r;" % (", ".join(fmt(14 + 208 * k) for k in range(1, R + 1)), R)),
    ("(222, 430, 638, 846, 1054, 1262, 1470 for 1..7 rounds)", "(14 + 208 r: %s for 1..%d rounds)" % (", ".join(str(14 + 208 * k) for k in range(1, R + 1)), R)),
    ("1,470", fmt(U)), ("1470", str(U)),
    ("45,974", fmt(info["ops"])), ("45974", str(info["ops"])), ("46,231", fmt(nodes)), ("46231", str(nodes)),
    ("1,755,288", fmt(code)), ("1755288", str(code)), ("1540", str(ph7)), ("2747", str(oc)),
    ("185752", str(2 * st.gen_calls)), ("92,876", fmt(st.gen_calls)), ("used up to 19 times", "used up to %d times" % maxuse), ("up to 19 times", "up to %d times" % maxuse),
    ("taken from four rounds to seven", "taken from four rounds to %s" % W), ("at seven rounds", "at %s rounds" % W), ("seven rounds", "%s rounds" % W),
    ("Our first entry for BLAKE3 at seven rounds, the full round count", "Our first entry for BLAKE3 at %s rounds" % W),
    ("to seven (BLAKE3 has seven rounds)", "to %s" % W), (", the full round count of BLAKE3", ""), ("(the target, the full round count)", "(a round count of this lane)"),
    ("at 3 rounds, at 4 rounds and at %d rounds" % 7, "at 3 rounds, at 4 rounds and at %d rounds" % R),
    ("at 3, 4 and 7 rounds", "at 3, 4 and %d rounds" % R), ("and at 7 rounds also with the `blake3` library", "and at 7 rounds also with the `blake3` library"),
]
files = []
for dp, dn, fn in os.walk(DST):
    for f in fn:
        if f.endswith((".py", ".md", ".c", ".sh")) and "pkg" not in dp.replace(DST, ""):
            files.append(os.path.join(dp, f))
files.append(os.path.join(X, "bsrho.py"))
tot = collections.Counter()
for fp in files:
    t = open(fp, encoding="utf-8", newline="").read()
    t0 = t
    base = os.path.basename(fp)
    t = open(os.path.join(SRC, os.path.relpath(fp, DST)), encoding="utf-8", newline="").read() if os.path.exists(os.path.join(SRC, os.path.relpath(fp, DST))) and base != "bsrho.py" else (s if base == "bsrho.py" else t)
    t = t.replace(chr(13) + chr(10), chr(10))
    for a, c in reps:
        n = t.count(a)
        if n:
            tot[a] += n
            t = t.replace(a, c)
    # round-specific constants in appA.py
    if base == "appA.py":
        t = re.sub(r"PH, FILT, LOOP, LANES = \d+,", "PH, FILT, LOOP, LANES = %d," % info["ops"], t)
        t = re.sub(r"GEN_CALLS = \d+ ", "GEN_CALLS = %d " % (2 * st.gen_calls), t)
        t = re.sub(r"PH7, EXTRA, PASSES = \d+,", "PH7, EXTRA, PASSES = %d," % ph7, t)
        t = re.sub(r"INSTR, OTHER_CODE, REGFILE", "INSTR, OTHER_CODE, REGFILE", t)
        t = re.sub(r"= 36, \d+, 800 \* 32", "= 36, %d, 800 * 32" % oc, t)
        t = re.sub(r"P, C = 100000, \d+", "P, C = 100000, %d" % U, t)
    open(fp, "w", encoding="utf-8", newline="").write(t)
# a second copy of the r7 text for files that were re-read from SRC above keeps their paths; report residuals
print({k: v for k, v in tot.items()})
for fp in files:
    t = open(fp, encoding="utf-8", newline="").read()
    for i, l in enumerate(t.split("\n"), 1):
        if re.search(r"\bseven\b|\br7\b|\b7 rounds|round 7|round-7|1[,]?912|0\.866|1,9[0-9][0-9],[0-9]{3}|29 pages|1437", l):
            print("RESIDUAL", os.path.relpath(fp, DST), i, l[:150])
