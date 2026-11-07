"""Assemble a filing package from the templates: python assemble.py VALUES.json SRC_DIR OUT_DIR

Reads proof_template.md, claim_template.json, note_template.md, experiments/ and certificates/ from this folder,
fills every @@NAME@@ placeholder from VALUES.json plus the values derived here from R, K, Q, N_BOUND and MEM_BYTES,
appends the complete source files named in VALUES["SOURCE_FILES"] (read from SRC_DIR) as the appendix of proof.md,
computes the proof line ranges that claim.json cites, and refuses to write anything while a placeholder is still
unfilled or a value still starts with TODO. It runs nothing from the source files and no experiment.
"""
import json, math, os, re, shutil, sys

HERE = os.path.dirname(os.path.abspath(__file__))
NUM = ["zero", "one", "two", "three", "four", "five", "six", "seven", "eight", "nine", "ten", "eleven", "twelve",
       "thirteen", "fourteen", "fifteen", "sixteen", "seventeen", "eighteen", "nineteen", "twenty", "twenty-one",
       "twenty-two", "twenty-three", "twenty-four", "twenty-five", "twenty-six", "twenty-seven", "twenty-eight",
       "twenty-nine", "thirty", "thirty-one", "thirty-two", "thirty-three", "thirty-four", "thirty-five",
       "thirty-six", "thirty-seven", "thirty-eight", "thirty-nine", "forty"]


def L(x): return '{:,}'.format(int(x))
def ceil5(x): return math.ceil(round(x * 100000, 6)) / 100000
def ceil3(x): return math.ceil(round(x * 1000, 6)) / 1000


def derive(v):
    R, K = int(v["R"]), int(v["K"])
    q = float(v["Q"])
    d = {}
    d["DEXP"] = 6 + R
    D = 5 ** d["DEXP"]
    m = (D - 1) // 2
    hexp = 0
    while (3 << hexp) < m + 1: hexp += 1
    aexp = 0
    while (3 << aexp) < 2 * m - 1: aexp += 1
    d.update(D=D, M=m, M1=m - 1, HEXP=hexp, H=3 << hexp, AEXP=aexp, VEXP=m.bit_length() - 1)
    d["N2"] = 2 * (3 << hexp)
    d["N2_HALF"] = L(3 << hexp)
    d["STEPS"] = 253 - d["VEXP"]
    d["C"] = 216 + 21 * R
    parts = [str(4 + i) for i in range(R)]
    d["PARTIALRS"] = ", ".join(parts)
    d["PARTIAL"] = "%s partial rounds %s" % (NUM[R], ", ".join(parts[:-1]) + " and " + parts[-1]) if R > 1 else "one partial round 4"
    d["PARTIAL_WORD"] = "%s partial rounds" % NUM[R] if R > 1 else "one partial round"
    d["LAYERS"] = NUM[6 + R]
    d["LINE"] = "0"
    for k in ("D", "M", "M1", "H", "N2"): d[k] = L(d[k])
    for k in ("DEXP", "HEXP", "AEXP", "VEXP", "STEPS", "C"): d[k] = str(d[k])
    if "N_BOUND" in v and not str(v["N_BOUND"]).startswith("TODO"):
        N = int(str(v["N_BOUND"]).replace(",", ""))
        te = math.log2(N / (216 + 21 * R))
        d["N_BOUND"] = L(N)
        d["UNITS"] = "{:,.1f}".format(N / (216 + 21 * R))
        d["TIME_LOG2_EXACT"] = repr(te)
        d["TIME_LOG2"] = "%.5f" % ceil5(te)
    if "MEM_BYTES" in v and not str(v["MEM_BYTES"]).startswith("TODO"):
        mb = int(str(v["MEM_BYTES"]).replace(",", ""))
        ml = ceil3(math.log2(mb))
        d["MEM_BYTES"] = L(mb)
        d["MEM_LOG2"] = "%.3f" % ml
        d["MEM_PEN"] = "%.3f" % (ml - 20)
        if "TIME_LOG2" in d: d["SCORE"] = "%.5f" % (ceil5(math.log2(N / (216 + 21 * R))) + round(ml - 20, 3))
    es = float(v.get("EPS_COIN_NUM", 2.0 ** -65)) + float(v.get("EPS_ISO_NUM", 2.0 ** -48))
    exact = 1 - (1 - q) ** K - K * es
    d["P_SUCC_EXACT"] = "%.9f" % exact
    d["P_SUCC"] = "%.5f" % (math.floor(exact * 100000) / 100000)
    d["EPS_SUM"] = "%.2e" % es
    qmin = 1 - 0.61 ** (1.0 / K)
    d["Q_MIN_K"] = "%.5f" % (math.ceil(qmin * 100000) / 100000)
    d["Q_RATIO_K"] = "%.3f" % (math.ceil(qmin * 100000) / 100000 / q)
    if exact < 0.39:
        sys.exit("derived success bound %.6f is below 0.39: raise K or fix Q" % exact)
    return d


def main(values_path, src_dir, out_dir):
    v = json.load(open(values_path, encoding="utf-8"))
    v = {k: x for k, x in v.items() if not k.startswith("_")}
    d = derive(v)
    vals = dict(d)
    vals.update({k: (x if isinstance(x, str) else str(x)) for k, x in v.items()})
    todo = [k for k, x in vals.items() if x.startswith("TODO")]
    if todo: sys.exit("unfilled TODO values: " + ", ".join(sorted(todo)))

    proof = open(os.path.join(HERE, "proof_template.md"), encoding="utf-8").read()
    files = v["SOURCE_FILES"]
    app = []
    for name in files:
        txt = open(os.path.join(src_dir, name), encoding="utf-8").read()
        app.append("### %s\n\n```c\n%s\n```" % (name, txt.rstrip("\n")))
    appendix = "\n\n".join(app)
    marker = "@@APPENDIX@@"

    def sub(text, extra=None):
        mp = dict(vals)
        if extra: mp.update(extra)
        return re.sub(r"@@([A-Z0-9_]+)@@", lambda m: mp[m.group(1)] if m.group(1) in mp else m.group(0), text)

    head = sub(proof.replace(marker, "")).rstrip("\n") + "\n\n"
    # line ranges of the sections the claim cites (computed on the final text)
    lines = (head + appendix).split("\n")
    def find(prefix, start=0):
        for i in range(start, len(lines)):
            if lines[i].startswith(prefix): return i
        sys.exit("heading not found: " + prefix)
    def rng(a, b):
        i, j = find(a), find(b)
        return "%d-%d" % (i + 1, j)
    ln = {"LN_PREMISE": rng("### 9.1", "### 9.2"), "LN_EVIDENCE": rng("### 10.1", "### 10.2"),
          "LN_LEDGER": rng("## 6.", "## 7."), "LN_SOURCE_HEAD": "%d-%d" % (find("## 11.") + 1, find("## 11.") + 3)}
    proof_out = head + appendix + "\n"
    left = sorted(set(re.findall(r"@@[A-Z0-9_]+@@", head)))
    claim = sub(open(os.path.join(HERE, "claim_template.json"), encoding="utf-8").read(), ln)
    note = sub(open(os.path.join(HERE, "note_template.md"), encoding="utf-8").read(), ln)
    left += sorted(set(re.findall(r"@@[A-Z0-9_]+@@", claim + note)))
    if left: sys.exit("unfilled placeholders: " + ", ".join(sorted(set(left))))
    json.loads(claim)
    if len(note.encode("utf-8")) < 5 * 1024: sys.exit("note is under 5 KiB")
    os.makedirs(out_dir, exist_ok=True)
    open(os.path.join(out_dir, "proof.md"), "w", encoding="utf-8", newline="\n").write(proof_out)
    open(os.path.join(out_dir, "claim.json"), "w", encoding="utf-8", newline="\n").write(claim)
    open(os.path.join(out_dir, "submission-note.md"), "w", encoding="utf-8", newline="\n").write(note)
    for sub_dir in ("experiments", "certificates"):
        dst = os.path.join(out_dir, sub_dir)
        if os.path.isdir(dst): shutil.rmtree(dst)
        shutil.copytree(os.path.join(HERE, sub_dir), dst, ignore=shutil.ignore_patterns("__pycache__"))
    tot = sum(os.path.getsize(os.path.join(out_dir, "experiments", f)) for f in os.listdir(os.path.join(out_dir, "experiments")) if f.endswith(".py"))
    print("written to", out_dir, "| proof bytes", len(proof_out.encode()), "| note bytes", len(note.encode()), "| experiment sources bytes", tot, "| lines", ln)


if __name__ == "__main__":
    if len(sys.argv) != 4: sys.exit(__doc__)
    main(*sys.argv[1:])
