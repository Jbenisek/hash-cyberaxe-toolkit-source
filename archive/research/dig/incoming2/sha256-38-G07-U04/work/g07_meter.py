# g07_meter.py - G07-U04 LEDGER.LM3 R2/R3: metered run of the shipped a0lean38.py process_fb on random first blocks.
# Rule written BEFORE the run: (1) every class that has 0 passing lanes costs exactly 7+15*(prog+6) metered ops (hard check, any mismatch = fail);
# (2) mean metered ops per first block minus the fixed 35 must lie within 3 sigma of vbar=132300.1864 (sampled, informational: heavy tail);
# (3) the w7-phase ops per first block (no hit list) must have mean within 3 sigma of w7 term 1497.66 (the exact control, known answer);
# (4) negative control: the same z test against 1.05 x 1497.66 must reject.

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

import sys, json, math, time, random
EXP = _hca_public_path_text('__HCA_WORKSPACE__/research/tools/build_pkg/scratch/pkgR38M3/pkg/sha256-r38/experiments')
sys.path.insert(0, EXP)
import a0lean38 as L
TL = float(sys.argv[1]) if len(sys.argv) > 1 else 600
rng = random.Random(20261012)
m = L.Mach(lambda: rng.getrandbits(256)); st = L.Stats()
rec = []; cls_nolane = 0; cls_nolane_bad = 0; lane_obs = []; classes_total = 0
orig_pc = L.process_class
def hooked(mm, ci, cv, fb, s, check=True):
    global cls_nolane, cls_nolane_bad, classes_total
    o0 = mm.ops; p0 = s.pre
    orig_pc(mm, ci, cv, fb, s, check)
    d = mm.ops - o0; k = s.pre - p0; classes_total += 1
    base = 7 + 15 * (len(L.program(L.GRP[ci])[0]) + 6)
    if k == 0:
        cls_nolane += 1
        if d != base: cls_nolane_bad += 1
    else:
        lane_obs.append((L.CLASSES[ci][2], k, d - base))
L.process_class = hooked
orig_fbs = L.fb_scalars
mark = {}
def fbh(mm, cv):
    mark['o'] = mm.ops
    return orig_fbs(mm, cv)
L.fb_scalars = fbh
t0 = time.time(); n = 0
while time.time() - t0 < TL and n < 20000:
    o0 = m.ops; mark.clear(); h0 = st.hits
    L.process_fb(m, st, False, False)
    tot = m.ops - o0
    w7 = mark['o'] - o0 if 'o' in mark else None
    rec.append((tot, w7, st.hits - h0)); n += 1
    if n % 200 == 0: print(n, round(time.time() - t0), flush=True)
tot = [r[0] - 35 for r in rec]
def stat(x):
    k = len(x); mu = sum(x) / k; v = sum((a - mu) ** 2 for a in x) / (k - 1); return mu, math.sqrt(v / k)
mu, se = stat(tot)
# w7-phase: for hit fbs, ops at fb_scalars entry minus start includes w7 loop + br + hit appends + 1; for no-hit fbs the whole total
# We compare the whole no-hit group exactly: ops of a no-hit fb = fixed 35 + w7 tests + 4/class loop (+br) ; expected per ledger: w7 term (1497.66, includes the +4 per class) - hmm 90*(12.640625+4)=1497.66
w7s = [(r[1] if r[1] is not None else r[0]) - 35 - (1 if r[1] is not None else 0) for r in rec]
mw, sw = stat(w7s)
res = dict(n_fb=n, seconds=round(time.time() - t0), mean_ops_minus_fixed=mu, se=se, vbar=132300.1864, z_vbar=(mu - 132300.1864) / se,
           w7_phase_mean=mw, w7_se=sw, w7_charged=1497.66, z_w7=(mw - 1497.66) / sw, z_neg_control=(mw - 1.05 * 1497.66) / sw,
           classes_total=classes_total, classes_no_lane=cls_nolane, classes_no_lane_mismatch=cls_nolane_bad,
           hits_per_fb=st.hits / n, fb_with_hit=sum(1 for r in rec if r[2] > 0) / n, passing_lanes=st.pre, row16=st.r16)
# lane cost observed per passing lane, vs charged max per mask
lm = {}
for mk, k, d in lane_obs:
    a = lm.setdefault(mk, [0, 0]); a[0] += k; a[1] += d
res['lane_obs'] = {str(mk): dict(lanes=a[0], ops_per_lane=a[1] / a[0]) for mk, a in lm.items()}
print(json.dumps(res, indent=1))
json.dump(res, open('g07_meter.json', 'w'), indent=1)
