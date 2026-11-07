"""Write RESULT.md from summary_relax*.out, check_relax0.out, sep.json and run.log."""
import json, os, re, sys
H = os.path.dirname(os.path.abspath(__file__)); os.chdir(H)
mode, logn = sys.argv[1], int(sys.argv[2])
BEST = 58.6198
cmin = {}
for R in (0, 2, 4):
    p = f"summary_relax{R}.out"
    if os.path.exists(p):
        m = re.search(r"^C\s+min\s+(\d+)\s+#patterns at min\s+(\d+)", open(p).read(), re.M)
        cmin[R] = (int(m.group(1)), int(m.group(2)))
sep = json.load(open("sep.json"))
runlog = open("run.log").read().strip()
check = open("check_relax0.out").read().strip()
t1, t2 = sep["T1 xor"], sep["T2 add"]
t3, t4 = sep["T3 word-pairs"], sep["T4 bit-pairs"]
conf_bits = len(t3["confirmed"]) + t4["confirmed_count"]
max_cell = max(t4["max_confirmed_bits_in_one_cell"], len(t3["confirmed"]))
strict_ok = cmin.get(0, (0, 0)) == (8, 65535)
relax_ok = all(cmin.get(R) == (7, 65535) for R in (2, 4))
nosep = conf_bits == 0 and t1["max_bias"] < 2 ** -8 and t2["max_bias"] < 2 ** -8 and sep["T2 add word==0 max frac"] == 0
join_bits = 16 * min(v[0] for v in cmin.values())
win = join_bits < BEST or max_cell >= 64
kill = strict_ok and relax_ok and nosep
L = [f"# basextech / mode / join - result ({mode} run, N = 2^{logn})", "",
     f"Reference self-check: parent compress == verifier blake3(rounds=2) {sep['selfcheck']}; rounds=7 and the "
     f"empty-input BLAKE3 test vector: {sep['selfcheck_r7']}.", "",
     "## (a) Exhaustive truncated model C, all 2^16 parent message patterns", ""]
for R, (mn, cnt) in sorted(cmin.items()):
    lab = {0: "strict", 2: "h1 may differ", 4: "h2 may differ"}[R]
    L.append(f"- RELAX {R} ({lab}): min {mn} word conditions ({32 * mn} bits), {cnt} patterns at the min")
L += ["", "```", runlog, "", check, "```", "",
      "## (b) Separability of the 2-round parent in (cvL, cvR)", "",
      f"- T1 XOR second derivative, all 256 bits, N=2^{logn}: max |P-1/2| = {t1['max_bias']:.6f} "
      f"(bit {t1['bit']}, {t1['max_bias'] / t1['sigma']:.2f} sigma); bits below 0.45: {t1['below_0.45']}",
      f"- T2 modular-add second derivative: max |P-1/2| = {t2['max_bias']:.6f} (bit {t2['bit']}); "
      f"max P(word == 0) = {sep['T2 add word==0 max frac']}",
      f"- T3 one word of L x one word of R (64 cells, {t3['n_per_cell']} quads each): worst |P-1/2| = "
      f"{t3['worst'][0]:.5f} ({t3['worst'][1]} bit {t3['worst'][2]}); flagged {t3['flagged']}, confirmed {len(t3['confirmed'])}",
      f"- T4 single-bit differences (1024 cells, {t4['n_per_cell']} quads each): worst |P-1/2| = "
      f"{t4['worst'][0]:.5f} ({t4['worst'][1]} bit {t4['worst'][2]}); flagged {t4['flagged']}, confirmed "
      f"{t4['confirmed_count']} in {t4['cells_with_confirmed']} cells (max {t4['max_confirmed_bits_in_one_cell']} bits in one cell)",
      "", "Flag rule: |P-1/2| >= 2^-8 and above a Bonferroni z threshold; a flag counts only if a 16x fresh re-measure keeps it.",
      "", "## Not computed (argued only)", "",
      "- The step from (a)+(b) to a cost: each surviving word condition is taken to cost >= 2^16 even through a "
      f"list match, giving >= 2^(16 x {min(v[0] for v in cmin.values())}) = 2^{join_bits}. That per-condition price is an argument, not a measurement.",
      "- The truncated model is word-level; bit-level partial cancellations inside a word are not modelled.",
      "", "## Verdict", "",
      f"VERDICT: {'SMOKE ONLY (RELAX 2/4 not run) - ' if mode == 'smoke' else ''}{'KILL met - close the cell by computation' if kill and not win else ('WIN - escalate' if win else 'INCONCLUSIVE')}. "
      f"Kill criterion (C min 8 strict / 7 relaxed, no separable bit): {'met' if kill else 'NOT met'}. "
      f"Win criterion (join cost < 2^{BEST} or >= 64 usable biased bits): {'met' if win else 'not met'} "
      f"(join-aware bound 2^{join_bits}, max confirmed biased bits in one cell {max_cell})."]
open("RESULT.md", "w").write("\n".join(L) + "\n")
