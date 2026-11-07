"""Write one JSON record per cell for units blake3-r3-U64..U72 (texts are ours; numbers come from the *_out.json / scan*.txt / psearch30.txt files in this folder)."""

# Publication path adapter: resolve data paths from the extracted source tree.
def _hca_public_path_text(value):
    if "__HCA_WORKSPACE__/" not in value:
        return value
    import os as _hca_os
    from pathlib import Path as _hca_Path
    root = _hca_os.environ.get("HASHCYBERAXE_WORKSPACE")
    if root is None:
        here = _hca_Path(__file__).resolve().parent
        root = next((str(p) for p in (here, *here.parents) if (p / "research").is_dir()), None)
    if root is None:
        raise FileNotFoundError("Extract the research source tree, or set HASHCYBERAXE_WORKSPACE to its archive directory.")
    return value.replace("__HCA_WORKSPACE__/", str(_hca_Path(root).resolve()).replace("\\", "/") + "/")

import json, os, math, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import eng
from eng import rho
WS = _hca_public_path_text('__HCA_WORKSPACE__/')
INC = os.path.join(WS, "research", "dig", "incoming3")
W = "research/dig/incoming3/blake3-r3-U64/work/"
E1 = json.load(open(os.path.join(INC, "blake3-r3-U64", "work", "exp1_out.json")))
UNI = {}
for l in open(os.path.join(WS, "research", "dig", "UNIVERSE.jsonl")):
    d = json.loads(l)
    if d["hash"] == "blake3-r3":
        UNI[d["id"]] = d


def tl2(ops):
    old = rho.PH; rho.PH = ops; lg = rho.ledger(256); rho.PH = old
    return math.log2(lg["total"] / 638)


B = tl2(595)
def dt(ops): return tl2(ops) - B
OP = B - tl2(594)
VAL = ("Validated first: own engine (eng.py) reproduces BLAKE3 7-round known vectors (inputs of length 0, 1, 2) and equals verifier/blake3.py on 140 cases "
       "(rounds 1..7, 20 lengths up to 8193 bytes, own chunk tree); the traced 7-lane SWAR circuit (rho.py Tracer, generalized) equals the own scalar compress "
       "on 7 lanes; baseline 3-round chain circuit = 595 ops = rho.py PH, time_log2 %.5f, one op = %.5f bit." % (B, OP))
SRC = "our workflow: dig-scan-b3r3"
recs = {}


def rec(unit, loc, q, labels, status, number, notes, held, reopen, evidence, lever=False, gain=None, basis="count", topic=None,
        pot=None, prior=None, obj_suffix=""):
    uid = "blake3-r3|%s|%s|%s" % (loc, loc.split(".")[0], q)
    u = UNI[uid]
    qtxt = {"Q1": "Q1: value/count as used", "Q2": "Q2: necessity (change it, recount the exact outcome)",
            "Q3": "Q3: degrees of freedom or score-optimal value", "Q4": "Q4: alternatives", "D1": "D1: RELABEL test of the r2 door at 3 rounds"}[q]
    r = dict(hash="blake3-r3", row_i=None, row_j=None, source=SRC, own_test=True, evidence=evidence, date="2026-10-12", lever=lever,
             gain_bits=gain, gain_basis=basis, object=u["label"] + obj_suffix, question=qtxt, labels=labels, status=status, number=number,
             topic=topic or ("b3r3.%s.%s" % (loc, q)), notes="universe cell %s. %s %s" % (uid, VAL, notes), held_fixed=held, reopen_if=reopen)
    if pot is not None:
        r["potential_bits"] = pot; r["prior"] = prior
    recs.setdefault(unit, {})[uid] = r


EV = W + "eng.py, exp1.py, exp1_out.json"
EVS = EV + ", scan.cpp, scan_joint.txt, scan0.txt, scan1.txt, scan2.txt"
HELD = ("target blake3-r3-prefix-v1; chain x -> digest(0^32||x) with identity embedding in m8..m15; 7-lane SWAR op model of rho.py (add/and/or/xor/shl/shr, constants folded, "
        "guard bits, masks as in the filed circuit); ledger of the filed entry (125.1087) with only PH changed")
HELD_D1 = "target blake3-r3-prefix-v1 compression at 1, 2 and 3 rounds; IV chaining value; counter 0; all 16 message words random 32-bit (not K = 0); pair = same words except the absorbing words; 1500 pairs (digest equality), 6000 pairs (bias)"
REO = "a legal value or layout that gives fewer than 595 ops per 7-lane batch, or a ledger line that charges a different count"

# ------------------------------------------------------------------ U64: INIT.v12..v15
u = "blake3-r3-U64"
rec(u, "INIT.v12", "Q2", ["N"], "COMPUTED",
    "Counter (low word) changed: ops of the 3-round chain circuit stay 595 for counters 0, 1, 2, 1023, 2^32, 2^64-1 and 300 random 64-bit values (time_log2 %.5f unchanged), "
    "because every round-0 column call is all-constant and folds. Exact scan of all 2^32 values of v12 (K = 0, other state words as in the target): v4' = 0 for exactly 1 value (201b8e14), "
    "v8' = 0 for 1 (41e5f136), v12' = 0 for 1 (ec448e39); no value zeroes two of the four column outputs (joint count 0). Each such zero would delete one immediate op (%.5f bit), but a root "
    "compression of one chunk has counter 0 by definition, so none of these values is available. The value 0 is forced by the target, not chosen for cost." % (B, OP),
    "Exact 2^32 scan (scan.cpp mode 0, OpenMP, nice 10, about 20 s per mode in WSL). The 16 immediate sites of the filed circuit are the diagonal-call constants v0'+v5', v5', v10', v15' (and the three rotations of that pattern); "
    "they are listed by imm.py logic in exp1.py/eng.py (8 add-imm, 8 xor-imm).",
    HELD, REO + ", or a legal chunk-index use where the counter reaches a root compression", EVS)
rec(u, "INIT.v12", "Q3", ["N", "K"], "COMPUTED",
    "No degree of freedom for a root compression (counter 0). Counterfactual domain 2^32: best single-value saving is 1 op (three different values give 1 op each, no value gives 2); "
    "legal score-optimal value is 0 with 595 ops. The apparent freedom of choosing a counter is fake for the cost: all counters give 595.",
    "Counter treated as a free 32-bit constant for the scan only; legal domain is {0}.", HELD, "a root-compression variant with a free counter word", EVS)
rec(u, "INIT.v12", "Q4", ["Z"], "COMPUTED",
    "Alternatives: a nonzero counter t >= 1 occurs only in a non-root chunk compression. Cheapest step of that kind = non-root last chunk block (counter 1, flags 3): 595 ops, then the parent root compression "
    "(flags 12, left CV nonzero constants, right CV variable): 611 ops; one chain step = %d ops, time_log2 %.4f (+%.4f bit over 125.1086). The counter itself never changes the op count (595 for every value). No alternative below 595." % (E1["G_modes"]["two_chunk_step"], tl2(E1["G_modes"]["two_chunk_step"]), dt(E1["G_modes"]["two_chunk_step"])),
    "Two-chunk message (1025+ bytes), left chunk constant, right chunk one block of 0^32||x.", HELD, "a tree host in which the counter-bearing compression is the root one", EV)

rec(u, "INIT.v13", "Q2", ["N"], "COMPUTED",
    "Counter (high word) changed: ops stay 595 (counter 2^32 and 2^64-1 tried, 300 random 64-bit values). Exact scan of all 2^32 values of v13: v5', v9', v13' (the three single-word fold sites of column 1) are never zero "
    "(counts 0, 0, 0); only a' = v1' is zero, for 1 value (b5fded32), and that matters only through the sum site v1' + v6' with a column-2 partner (pair count not enumerated, about 2^32 pairs expected). "
    "Counter high word is 0 for every legal root compression.",
    "Exact 2^32 scan (scan.cpp mode 0, col 1).", HELD, REO, EVS)
rec(u, "INIT.v13", "Q3", ["N", "K"], "COMPUTED",
    "No freedom (0 for a root compression); in the counterfactual 2^32 domain no value deletes a single-word site, so even a free v13 would save 0 ops alone. Score-optimal legal value 0 (595 ops).",
    "Counterfactual only.", HELD, "a pair (v12,v13) or (v13,v14) that is legal and zeroes a sum site", EVS)
rec(u, "INIT.v13", "Q4", ["Z"], "COMPUTED",
    "Alternative: chunk index t >= 2^32 (needs a 4 TiB message): same cost as INIT.v12 Q4 (%d ops per step) and the same 595 op count of the counter-bearing compression. No gain." % E1["G_modes"]["two_chunk_step"],
    "As INIT.v12 Q4.", HELD, REO, EV)

rec(u, "INIT.v14", "Q2", ["N"], "COMPUTED",
    "Block length changed: ops stay 595 for every block length 1..64 (traced, 64 values), so v14 as a constant costs nothing either way. Exact scan of all 2^32 values of v14: v6' = 0 for blen = 9effdf77 and "
    "v10' = 0 for blen = c248160c (both far above 64, not legal); v14' never zero. The length is not free: the 32 bytes of x fix the layout, and the layout fixes the length (PIN.BLEN, PIN.X): "
    "x in words s..s+7 gives blen = 4s + 32 and ops 706, 691, 680, 666, 653, 636, 624, 610, 595 for s = 0..8.",
    "Exact scan col 2 (mode 0) plus the layout table of exp1.py section D.", HELD, "a legal length above 64 is impossible; reopen only if a one-block layout with fewer ops exists", EVS)
rec(u, "INIT.v14", "Q3", ["N"], "COMPUTED",
    "Score-optimal value: 64 (x occupying m8..m15), 595 ops; every shorter aligned length costs 15 to 111 more ops because zero padding words in front make the first-round column calls variable. "
    "Degrees of freedom: 9 aligned layouts (s = 0..8), one optimum.",
    "Aligned layouts only; zero constants for all words not holding x.", HELD, "a non-aligned layout cheaper than 595 (traced lower bound for s = 7 with a byte shift: 644)", EV)
rec(u, "INIT.v14", "Q4", ["Z"], "COMPUTED",
    "Alternatives: the 55/63 length pair of the 2-round line is a differential device (cancellation in call K2 through m4/m5), not a cost lever at 3 rounds: with the cancel the round-0 state is equal but the "
    "message words m4, m5 differ again in rounds 1 and 2; measured under DOOR.d22 (6000 pairs, no biased digest bit left at 3 rounds). Unaligned layouts (x shifted by 1..3 bytes): 644 ops (traced, includes the shift code).",
    "See DOOR.d22.", HELD, REO, EV + ", exp_d1b.py, exp_d1b_out.json")

rec(u, "INIT.v15", "Q2", ["N"], "COMPUTED",
    "Flags word changed: ops stay 595 for flags in {1,2,3,4,8,10,11,12,13,14,15,16,32} (traced). Exact scan of all 2^32 values of v15: v7', v11', v15' never zero (counts 0, 0, 0); only a' = v3' is zero (1c8bc0b9), "
    "usable only through the sum site v3' + v4'. Flags are fixed by the structure: one-block root = CHUNK_START|CHUNK_END|ROOT = 11; last block of a longer chunk = 10; parent root = 12.",
    "Exact scan col 3 (mode 0).", HELD, REO, EVS)
rec(u, "INIT.v15", "Q3", ["N"], "COMPUTED",
    "No freedom beyond the three legal root values 11 (single block), 10 (last block of a multi-block chunk), 12 (parent). Their costs: 595, 595 (any constant chaining value), 611 (left CV nonzero constants). "
    "Optimal flags value by cost: 11 or 10 (equal), 10 allows the chaining-value lever of MODE.last (594).",
    "Legal root flag values only.", HELD, REO, EV)
rec(u, "INIT.v15", "Q4", ["Z"], "COMPUTED",
    "Alternative flags 10 with a prefix block: same 595 ops and a free 256-bit chaining value; see MODE.last Q4 for the one-op lever it opens (594). Flags 12 (parent): 611 ops with right CV variable, 730 with left CV variable.",
    "See MODE.last.", HELD, REO, EV)

# ------------------------------------------------------------------ U65: PIN
u = "blake3-r3-U65"
C = E1["C_K"]
rec(u, "PIN.K", "Q2", ["N", "K"], "COMPUTED",
    "Key words m0..m7 changed from 0 to nonzero: each nonzero word adds exactly 2 ops (it is added once in round 1 and once in round 2): any single word %d, two words %d, all eight words %d ops "
    "(vs 595); 612 = swar_count.py figure. Cost of nonzero K over the filed K = 0: +%.4f bit for all eight words. In round 0 the K words only enter all-constant column calls, so they cost nothing there." % (C["K0_nonzero"], C["K_two_words_col0"], C["K_all8_nonzero"], dt(C["K_all8_nonzero"])),
    "Random nonzero 32-bit words; message layout x in m8..m15.", HELD, REO, EV)
rec(u, "PIN.K", "Q3", ["N", "K"], "COMPUTED",
    "Score-optimal value K = 0 (595 ops). Could a nonzero K delete fold sites instead? Exact scans of one K word (m_{2j}, y = 0) over 2^32 values: column 0 zeroes v4' for 1 value, v8' for 1, v12' for 2 (v0' for 2), "
    "columns 1..3 zero at most one single site each (col 1: none, col 2: v10', col 3: v11' for 3 values); no value zeroes two outputs of a column. So one nonzero word saves at most 1 op and costs 2 (net +1), "
    "two words save at most 2 per column and cost 4. Zero degrees of freedom worth keeping: K = 0 is optimal for cost.",
    "Single-word exact scan (scan.cpp mode 1); two-word case by bounding (3 single sites per column, 2 ops per nonzero word).", HELD,
    "a K with several nonzero words whose joint saving exceeds 2 ops per word (needs more than 3 deleted sites per column pair, impossible by site count)", EVS)
rec(u, "PIN.K", "Q4", ["Z"], "COMPUTED",
    "Alternatives: (1) other constants for the 32 prefix bytes: +2 ops per nonzero word (above). (2) A shorter prefix with x moved forward (blen < 64, trailing zero padding): 610..706 ops. "
    "(3) Replace the prefix by a chaining value from a prefix block (MODE.last): 595 with a free 256-bit CV, one op saved when the CV is tuned (594). Nothing below 594 found.",
    "As above.", HELD, REO, EV)

rec(u, "PIN.X", "Q2", ["N", "K"], "COMPUTED",
    "Placement of x changed. x in words s..s+7 (rest zero, blen = 4s+32): ops %s for s = 0..8; the filed s = 8 is the unique minimum. All 16 words variable: 730 ops. Unaligned (x shifted 1..3 bytes, s = 7, 9 words touched with shifts): 644 ops. "
    "Fewer variable words is impossible: the chain feeds all 256 digest bits back (identity embedding) and fewer input bits would make the iterated map not a map on the digest space." %
    "/".join(str(E1["D_place"]["s%d" % s]["ops"]) for s in range(9)),
    "Aligned layouts traced and checked against scalar compress (check true for all nine).", HELD, REO, EV)
rec(u, "PIN.X", "Q3", ["N", "K"], "COMPUTED",
    "256 free bits, all required: eight 32-bit words. Which digest word goes to which slot is a wiring choice with no op cost (not separately traced; register renaming); the start slot s = 8 is the optimum. "
    "Value freedom is only the start point r (one random word) of the chain.",
    "Identity embedding digest word i -> slot m(8+i).", HELD, "an embedding of fewer than 256 bits that still yields a digest collision with probability 1 per tag collision", EV)
rec(u, "PIN.X", "Q4", ["Z"], "COMPUTED",
    "Alternatives: x in the first 8 words (s = 0, 706 ops), middle placements 610..680, byte-shifted 644; a 64-byte x (all 16 words, 730 ops) gives 512 input bits of which only 256 can be fed back. None below 595.",
    "As Q2.", HELD, REO, EV)

rec(u, "PIN.BLEN", "Q2", ["N"], "COMPUTED",
    "Length 64 is the layout 0^32 || x with x in m8..m15. Changing the length changes the layout (x must keep 32 bytes): blen = 4s + 32 gives 706 .. 595 ops (s = 0..8); a bare constant change of v14 (blen 1..64) leaves 595. "
    "So 64 is needed for the cheapest layout, not for the digest.",
    "Table of exp1.py section D.", HELD, REO, EV)
rec(u, "PIN.BLEN", "Q3", ["N"], "COMPUTED",
    "Score-optimal value 64 (595 ops); the other eight aligned values are 15 to 111 ops worse (36: 691, 40: 680, 44: 666, 48: 653, 52: 636, 56: 624, 60: 610, 32: 706). Legal lengths that are not word multiples force byte shifts (644 traced for blen 61..63).",
    "Aligned lengths 32..64 step 4, plus s = 7 unaligned.", HELD, REO, EV)
rec(u, "PIN.BLEN", "Q4", ["Z"], "COMPUTED",
    "Alternatives: lengths 55/63 (differential pair) are not a generic-cost alternative; longer messages go to the multi-block modes (MODE.last 595, MODE.first and MODE.mid 1277, MODE.parent 611, trees 1206 and up). No length below 595 ops.",
    "As Q3.", HELD, REO, EV)

rec(u, "PIN.FLG", "Q2", ["N"], "COMPUTED",
    "Flags 11 changed to any other value: ops stay 595 (13 values traced); the digest function changes (different target), not the circuit cost. 11 is forced by one block, one chunk, root, unkeyed.",
    "Traced values {1,2,3,4,8,10,11,12,13,14,15,16,32}.", HELD, REO, EV)
rec(u, "PIN.FLG", "Q3", ["N", "K"], "COMPUTED",
    "No freedom inside the single-block mode; the freedom exists only by changing the mode: 10 (last block, free CV) and 12 (parent). Costs in ops: 595 / 595 / 611.",
    "Legal flag values.", HELD, REO, EV)
rec(u, "PIN.FLG", "Q4", ["S"], "COMPUTED",
    "Alternative flags 10 with a constant prefix block P (message P || 0^32 || x, 128 bytes): same circuit, the chaining value becomes a free 256-bit constant, and a P found by an offline search of 2^30 trials (43 s, 8 threads) "
    "deletes one immediate: 594 ops, time_log2 %.5f (-%.5f). Verified end to end against verifier/blake3.py at 3 rounds. Full record at MODE.last Q4 (lever recorded there once)." % (tl2(594), OP),
    "See MODE.last Q4.", HELD, "two or more sites deleted (needs about 2^57 trials by search; no cheaper search known to us)", EV + ", psearch.cpp, psearch30.txt, plever.py, plever_out.json")

# ------------------------------------------------------------------ U66/U67: OUT.d0..d7
F = E1["F_out"]
for unit, ids in (("blake3-r3-U66", range(0, 4)), ("blake3-r3-U67", range(4, 8))):
    for i in ids:
        only, without = F["only_d%d" % i], F["without_d%d" % i]
        rec(unit, "OUT.d%d" % i, "Q2", ["N", "K"], "COMPUTED",
            "Digest word %d dropped from the comparison: not allowed (the target needs all 256 output bits equal), and not usable inside the chain either (the next input is the whole digest). "
            "Counterfactual cost only: dead-code elimination of the traced circuit without word %d leaves %d ops (saves %d, %.5f bit)." % (i, i, without, 595 - without, dt(595) - dt(without)),
            "Counterfactual op count by dead-code elimination (eng.py trace dce=True).", HELD, "a target or embedding in which word %d is not compared or not fed back" % i, EV)
        rec(unit, "OUT.d%d" % i, "Q3", ["N", "K"], "COMPUTED",
            "No degree of freedom: all eight words are compared and all eight are fed back. Computing only word %d costs %d ops of 595 (%d ops are shared with the other words), which could matter only for a filter that tests this word "
            "before the rest is needed; the chain needs the full digest at every step, so there is no early exit." % (i, only, only),
            "Single-output dead-code elimination.", HELD, "a chain whose next input needs fewer than 8 digest words", EV)
        rec(unit, "OUT.d%d" % i, "Q4", ["Z"], "COMPUTED",
            "Alternatives: compare word %d in a staged way (compute it first: %d ops, then the other 7 words: %d more): no saving because every step continues from the full digest (595 total). "
            "Distinguished-point test uses digest word 0 only (low 32 bits of the 114 tested) and costs 4 ops per batch in the ledger already." % (i, only, 595 - only),
            "As Q3.", HELD, REO, EV)

# ------------------------------------------------------------------ U68: OUT.hi
u = "blake3-r3-U68"
rec(u, "OUT.hi", "Q2", ["N"], "COMPUTED",
    "The second half v[i+8] ^ h[i] is not in the digest and the filed circuit does not compute it. Adding it would cost +12 ops (607 vs 595, traced), +%.4f bit. Not necessary."
    % (dt(607)), "Traced with hi=True (eng.py), checked against scalar compress.", HELD, REO, EV)
rec(u, "OUT.hi", "Q3", ["N"], "COMPUTED",
    "No freedom: the profile fixes the digest to the first 32 root-output bytes. Optimal: do not compute the high half (595).", "Profile fact.", HELD, "a longer output in the profile", EV)
rec(u, "OUT.hi", "Q4", ["Z"], "COMPUTED",
    "Alternatives: none inside the profile (extended output is not part of blake3-r3-prefix-v1). The high half would only add checks that the generic attack does not need.", "Profile fact.", HELD, "a profile with extended output", EV)

# ------------------------------------------------------------------ U69/U70/U71: MODE
G = E1["G_modes"]
LEVER_NUM = ("Chaining value h tuned by a prefix block. Search: 64-byte block P (words P0 = t, P1 = t >> 32, rest 0), h = first 8 words of the 3-round non-root compression of P (counter 0, length 64, flags 1); "
             "the next block (flags 10, message 0^32 || x) has 16 constant-fold sites (12 single words b', c', d' of the four round-0 columns, 4 sums). 2^30 trials, 43 s on 8 threads at nice 10: 5 hits "
             "(expected 16 * 2^30 / 2^32 = 4): t = 887398322 (site v0'+v5'), 214938249 (v12'), 639130335 (v14'), 939343106 (v0'+v5'), 508565131 (v13'). For each: the traced circuit with cv = h, flags 10 has 594 ops, "
             "equals the scalar compress, and the circuit output equals verifier/blake3.py at 3 rounds for 210 random messages P || 0^32 || x per hit (128-byte messages, two blocks). "
             "time_log2 %.5f vs %.5f: saving %.5f bit. Two sites need about 2^64 / C(16,2) = 2^57 trials by this search; not run." % (tl2(594), B, OP))
u = "blake3-r3-U69"
rec(u, "MODE.single", "Q2", ["N"], "COMPUTED",
    "Single-block root is the filed mode (595 ops). Changing the mode: last block of a multi-block chunk 595 (same), parent root 611, first/mid block with variable chaining value 1277, two-chunk tree 1206. "
    "So single block is not needed for cost, but nothing is cheaper.",
    "Chain step cost with the same op model; see MODE.* cells.", HELD, REO, EV)
rec(u, "MODE.single", "Q3", ["N", "K"], "COMPUTED",
    "No constants to choose (IV, counter 0, flags 11, length 64, K = 0): 0 degrees of freedom; optimum 595.", "Single-block mode.", HELD, REO, EV)
rec(u, "MODE.single", "Q4", ["S"], "COMPUTED",
    "Alternative that beats it: the two-block mode with a tuned prefix block, 594 ops (-%.5f bit); see MODE.last Q4." % OP, "See MODE.last.", HELD, REO, EV)

rec(u, "MODE.first", "Q1", ["N"], "COMPUTED",
    "Not used by the filed entry. Count if the variable block is the first block of a two-block chunk (CHUNK_START, IV) and the last block is constant: block 1 = %d ops (flags 1), block 2 with variable chaining value and constant zero message = %d ops; chain step %d ops, time_log2 %.4f (+%.4f bit)."
    % (G["first_var_then_const_last"]["first"], G["first_var_then_const_last"]["last_cvvar"], G["first_var_then_const_last"]["total"], tl2(G["first_var_then_const_last"]["total"]), dt(G["first_var_then_const_last"]["total"])),
    "x in m8..m15 of the first block, K = 0, second block all-zero message, flags 10.", HELD, REO, EV)
rec(u, "MODE.first", "Q2", ["N"], "COMPUTED",
    "Necessity: not needed; changing to a variable first block adds the whole second compression with variable state (682 ops, no folding): 1277 vs 595.",
    "As Q1.", HELD, REO, EV)
rec(u, "MODE.first", "Q3", ["N", "K"], "COMPUTED",
    "Freedom: the final block's message words (512 bits) are free constants but nonzero ones add ops (every word is variable-state anyway: 682 for zeros); no choice lowers the sum below 1277 because the second compression has no constant state to fold.",
    "As Q1.", HELD, REO, EV)
rec(u, "MODE.first", "Q4", ["N"], "OPEN",
    "Alternative lines for this mode (door 45: 224-bit near-collision of the first block, then a free final block; B3R3-C1) were not redone here. Generic cost of the mode is 1277 ops per step, so only a structural line could use it. "
    "OPEN, not tested at 3 rounds beyond the op count.",
    "Generic birthday cost only.", HELD, "a differential or near-collision line with success per step above 2^-128 * 1277/595 relative", EV, pot=0.0, prior=0.02)

rec(u, "MODE.mid", "Q1", ["N"], "COMPUTED",
    "Not used. Variable middle block (cv constant from a prefix block, flags 0), then a constant last block with variable chaining value: %d + %d = %d ops per step (time_log2 %.4f, +%.4f bit)."
    % (G["mid_var"]["mid"], G["mid_var"]["last_cvvar"], G["mid_var"]["total"], tl2(G["mid_var"]["total"]), dt(G["mid_var"]["total"])),
    "As MODE.first with a constant first block.", HELD, REO, EV)
rec(u, "MODE.mid", "Q2", ["N"], "COMPUTED",
    "Necessity: not needed. The middle block fixes only the chaining value constants (any random constants give 595); the variable-state last block costs 682.", "As Q1.", HELD, REO, EV)
rec(u, "MODE.mid", "Q3", ["N", "K"], "COMPUTED",
    "Freedom: chaining value of the middle block (256 bits), no effect on the 595 op count (300 random CVs all 595); only the zero-site lever applies, and only when the variable block is the LAST one (MODE.last).",
    "As Q1.", HELD, REO, EV)
rec(u, "MODE.mid", "Q4", ["Z"], "COMPUTED",
    "Alternatives: fresh CV per context (door 37) costs nothing in ops when the variable block is the last block (595); when the variable block is in the middle the extra block makes it 1277. No gain from the middle position.",
    "As Q1.", HELD, REO, EV)

u = "blake3-r3-U70"
rec(u, "MODE.last", "Q1", ["N"], "COMPUTED",
    "Not used by the filed entry (single block). Count: last block of a two-block chunk (flags 10), constant prefix block, variable 0^32 || x: %d ops with any constant chaining value (300 random CVs all 595), so mode-neutral." % G["last_var_const_prefix"],
    "Constant prefix block, chain on the last block.", HELD, REO, EV)
rec(u, "MODE.last", "Q2", ["N"], "COMPUTED",
    "Necessity: the last block is the only position where the variable block costs 595; first and mid cost 1277. Replacing the single block by prefix + last block changes nothing in the op count.", "As Q1.", HELD, REO, EV)
rec(u, "MODE.last", "Q3", ["S"], "COMPUTED",
    "Degrees of freedom: a 256-bit chaining value h (the 512-bit prefix block maps to it). 16 fold sites (12 single words, 4 sums); each zero deletes one op (%.5f bit). A random h has a given site zero with probability 2^-32, "
    "so any-of-16 costs about 2^28 trials per site found. With one chaining word free and its partner fixed some sites have no solution (exact scans: column 1 b', c', d' none), but the search over whole h found sites v12', v13', v14' and the sum v0'+v5'. Optimum found: 594 ops (k = 1)." % OP,
    "First block flags 1 (CHUNK_START), counter 0, length 64; second block flags 10.", HELD, "k >= 2 sites deleted: about 2^57 trials by random search; a structured preimage on the 3-round compression for a chosen h could make several sites cheap (OPEN)", EV + ", psearch.cpp, psearch30.txt, plever.py, plever_out.json")
rec(u, "MODE.last", "Q4", ["S"], "COMPUTED", LEVER_NUM,
    "LEVER (small): applies to the filed 125.1087 entry as a change of message layout (two blocks, flags 10) and a 64-byte constant prefix block; the ledger gets the same terms except PH 594 and one extra constant compression done offline (setup 2000 already covers constants). "
    "Caveats: not run through rho.py end to end with a two-block message (circuit and verifier agree); judge acceptance of a 128-byte pair not tested; the prefix search is advice (2^30 work) and the entry would have to state it.",
    HELD, "k = 2: 2^57-trial search or a structured preimage; or a ruling that the advice/prefix block is charged more than 2^30 compressions",
    EV + ", psearch.cpp, psearch30.txt, plever.py, plever_out.json, scan_joint.txt", lever=True, gain=round(OP, 5), basis="T")

rec(u, "MODE.ctr", "Q1", ["N"], "COMPUTED",
    "Not used. A chunk index t >= 1 reaches only non-root chunk compressions: cost of the counter-bearing compression 595 (flags 3, counter 1; any counter gives 595); with the parent root above it one step is %d ops (time_log2 %.4f)."
    % (G["two_chunk_step"], tl2(G["two_chunk_step"])), "Two-chunk tree.", HELD, REO, EV)
rec(u, "MODE.ctr", "Q2", ["N"], "COMPUTED",
    "Necessity: not needed; the root compression's counter is 0 in every mode and the op count does not depend on any counter value. A counter t only forces the parent level (+611 ops).", "As Q1.", HELD, REO, EV)
rec(u, "MODE.ctr", "Q3", ["N", "K"], "COMPUTED",
    "Freedom: t is any 64-bit value, with no effect on the cost (all tested counters 595); the exact scans show a counter word could delete one fold site, but only in a root compression, where it is 0.", "As Q1.", HELD, REO, EVS)
rec(u, "MODE.ctr", "Q4", ["Z"], "COMPUTED",
    "Alternative: the filed B3V line (last-chunk half-collision with a counter search) is a 1-round/2-round device; at 3 rounds the counter has no cost effect and the tree makes each step 1206+ ops. No gain.", "As Q1.", HELD, REO, EV)

rec(u, "MODE.parent", "Q1", ["N"], "COMPUTED",
    "Not used. Parent root (flags 12, left CV nonzero constants, right CV variable): %d ops (K nonzero costs +16); with the left CV variable: %d ops. One chain step (child chunk %d + parent): %d (right), %d (left)."
    % (G["parent_root_var_right"], G["parent_root_var_left"], G["chunk_t1_nonroot"], G["two_chunk_step"], G["two_chunk_step_varleft"]), "Random nonzero CV words.", HELD, REO, EV)
rec(u, "MODE.parent", "Q2", ["N"], "COMPUTED",
    "Necessity: not needed; the parent mode needs the child CV as input, so the chain cannot feed digest to message directly: every step pays the child compression (595) plus the parent. Cheapest %d ops." % G["two_chunk_step"], "As Q1.", HELD, REO, EV)
rec(u, "MODE.parent", "Q3", ["N", "K"], "COMPUTED",
    "Freedom: the left CV words (a hash output); each zero word saves 2 ops but costs 2^32 work to find a left subtree with that word zero. Even all 8 zero (2^256) leaves 595 + 595 = 1190 per step. No point.", "As Q1.", HELD, REO, EV)
rec(u, "MODE.parent", "Q4", ["N"], "OPEN",
    "Alternatives: doors 3, 23 and 38 (differences between CVs or tree shapes) stay CLAIMED-UNTESTED; we measured only generic step cost (>= 1206 ops). Not tested: any differential line through a parent node at 3 rounds.",
    "Generic birthday step cost only.", HELD, "a parent-node difference with a closing probability above 2^-128 * 1206/595", EV, pot=0.0, prior=0.02)

u = "blake3-r3-U71"
rec(u, "MODE.tree", "Q1", ["N"], "COMPUTED",
    "Not used. Chain step with the variable chunk at depth d under the root: 595 + 611 d ops (d = 1: %d, d = 2: %d); variable chunk on the left side of the parent: %d (d = 1). time_log2 for d = 1: %.4f."
    % (G["two_chunk_step"], G["three_level_step"], G["two_chunk_step_varleft"], tl2(G["two_chunk_step"])), "Left subtrees constant.", HELD, REO, EV)
rec(u, "MODE.tree", "Q2", ["N"], "COMPUTED",
    "Necessity: not needed; any tree with more than one node makes the chain step at least %d ops (+1.01 bit). Single node is the optimum." % G["two_chunk_step"], "As Q1.", HELD, REO, EV)
rec(u, "MODE.tree", "Q3", ["N", "K"], "COMPUTED",
    "Freedom: tree shape and which leaf varies; the cheapest tree step is d = 1 with the variable chunk on the right (%d ops); every extra level adds 611." % G["two_chunk_step"], "As Q1.", HELD, REO, EV)
rec(u, "MODE.tree", "Q4", ["N"], "OPEN",
    "Alternatives: Opus cloud job 2 left no report on disk and door 3 excludes trees; our own count gives only the generic step cost. A tree-based differential was not tested at 3 rounds.", "Generic step cost only.", HELD, "a tree difference line with a per-step closing probability above 2^-128 * 1206/595", EV, pot=0.0, prior=0.02)

rec(u, "MODE.len", "Q2", ["N"], "COMPUTED",
    "Length pair (55, 63) and other pairs: the pair is needed only for the 2-round cancellation. For the generic chain one length (64) is used and any length 1..64 as a bare constant gives 595; no pair is needed.",
    "Bare constant scan, blen 1..64.", HELD, REO, EV)
rec(u, "MODE.len", "Q3", ["N"], "COMPUTED",
    "Freedom: 64 legal lengths as constants (all 595) but only the aligned layouts s = 0..8 keep x whole; best 64. Legal XOR differences between two lengths: any; their cancellation cost in the differential line is measured at DOOR.d22.", "As INIT.v14.", HELD, REO, EV)
rec(u, "MODE.len", "Q4", ["Z"], "COMPUTED",
    "Alternative pairs: for every pair a cancellation in column 2 (m4/m5) makes the round-0 state equal and leaves no biased digest bit at 3 rounds (6000 pairs, 55/63 tested); no pair gives a cheaper path than the generic 125.1086.",
    "Pair 55/63, random states.", HELD, REO, EV + ", exp_d1b.py, exp_d1b_out.json")

# ------------------------------------------------------------------ U72: DOORS
u = "blake3-r3-U72"
D1c = json.load(open(os.path.join(INC, "blake3-r3-U64", "work", "exp_d1c_out.json")))
D1b = json.load(open(os.path.join(INC, "blake3-r3-U64", "work", "exp_d1b_out.json")))
D1 = json.load(open(os.path.join(INC, "blake3-r3-U64", "work", "exp_d1_out.json")))
rec(u, "DOOR.d21", "D1", ["Z"], "SAMPLED",
    "Relabel at 3 rounds (flags 11 vs 12, delta 7). (a) Conservative word-level activity simulation (a call is active if any input differs; all four outputs then differ): without absorption 5, 8, 8 active G calls in rounds 0, 1, 2 and 8 of 8 digest words active, "
    "i.e. 8 conditions = 256 bits (the claim holds at 3 rounds). Delta 7 touches column 3 and all four diagonals. (b) With the exact in-call cancellation by m6/m7 (a1' = a1 ^ 7, m6' = m6 + e, m7' = m7 - e): round-0 state equal, "
    "0, 6, 8 active calls, 8 of 8 digest words active at 3 rounds (8 equal at 1 round). (c) Exact digest pairs, 1500 random messages: 0 equal digest words at rounds 1 (uncancelled), 2 and 3; cancelled: 8 equal at 1 round, 0 at 2 and 3. "
    "(d) Bias of the 256 digest difference bits, 6000 pairs: uncancelled r1 63 biased bits, r2 and r3 none; cancelled r1 256, r2 17 biased bits in 4 words (max deviation 0.14), r3 none (max deviation 0.018, below the 0.05 threshold). "
    "At 3 rounds the flag door leaves no usable structure: 256-bit residual against 128 for birthday.",
    "Test: own pairs (m, flags 11) vs (m', flags 12), m' = m except m6/m7 (cancelled variant); other state words as the target; deviation threshold 0.05 = 7.7 sigma at 6000 pairs. "
    "Statistical power: a structure with a digest-bit bias below 0.05 would not show.",
    HELD_D1 + "; legal flag pair is single-block (11) vs parent root (12); parent words are CVs, so the shared-message pair is a model, not a legal pair",
    "a bias above 0.05 in any digest difference bit at 3 rounds for a legal pair, or a pair of legal messages realizing the absorption with ledger cost below 2^-128 per attempt",
    W + "eng.py, exp_d1.py, exp_d1_out.json, exp_d1b.py, exp_d1b_out.json, exp_d1c.py, exp_d1c_out.json",
    obj_suffix=" (3-round test)")
rec(u, "DOOR.d22", "D1", ["Z"], "SAMPLED",
    "Relabel at 3 rounds (two structural differences cancelling each other). Enumeration of in-call absorption over the four state words v12..v15 (each absorbed in its own column by two message words; sets D = {m0,m1}, {m2,m3}, {m4,m5}, {m6,m7}): "
    "(a) absorption with ZERO message difference is impossible: G is a bijection of the state for fixed message words (inverse verified on 200000 random states; 0 equal outputs in 300000 pairs differing only in d). "
    "(b) Absorption with message differences works in every column and every combination: round-0 state equal (8 of 8 digest words equal at 1 round) for length alone (55/63), flags alone, length+flags (D = m4..m7, 4 message words differ), counter lo+hi, and all four; "
    "at 2 and 3 rounds 0 digest words equal in 1500 random pairs each. Absorbing only one of two differences leaves the other: 0 equal at 1 round. "
    "(c) Word-level activity: length+flags absorbed: 0, 7, 8 active calls, 8 of 8 digest words active at 3 rounds (unabsorbed 6, 8, 8). "
    "(d) Bias test, 6000 pairs: length alone r2 64 biased bits in 7 words (max 0.32), r3 none; length+flags r2 none, r3 none. Smallest residual that meets legality is 256 bits (8 words) at 3 rounds, 0 solutions of full in-call absorption: the r2 claim reproduces and gets no better at 3 rounds.",
    "Legal pairs only when both messages are legal; counter pairs are not legal for root compressions (shown as a model). Message differences re-enter later rounds (m4..m7 reused in rounds 1 and 2).",
    HELD_D1, "a legal pair with fewer than 8 active digest words at 3 rounds, or a bias above 0.05 at 3 rounds",
    W + "eng.py, exp_d1.py, exp_d1_out.json, exp_d1b.py, exp_d1b_out.json, exp_d1c.py, exp_d1c_out.json",
    obj_suffix=" (3-round test)")

# ------------------------------------------------------------------ write
n = 0
for unit, d in recs.items():
    for uid, r in d.items():
        os.makedirs(os.path.join(INC, unit), exist_ok=True)
        path = os.path.join(INC, unit, uid.replace("|", "_") + ".json")
        json.dump(r, open(path, "w"), indent=1)
        n += 1
print("wrote", n, "records")
