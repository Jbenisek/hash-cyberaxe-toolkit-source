# g07_judge.py - G07-U04 JUDGE.JH4A: H4a / H4 allowance-characteristic-search cause across all stored r38 judge dossiers + the current package R38M3.

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

import json, glob, math, os
D = _hca_public_path_text('__HCA_WORKSPACE__/research/dossiers')
rows = []
for f in sorted(glob.glob(D + '\*\judge-dossier.json')):
    j = json.load(open(f, encoding='utf-8')); c = j['claim']
    if c.get('rounds') != 38 and 'r38' not in json.dumps(c)[:6000]: continue
    cl = c['claim']; a = j['aggregate']
    ids = [h['id'] for h in c['heuristics'] if h['id'].startswith('H4')]
    form = 'split' if any(i.startswith('H4a') for i in ids) else 'single'
    hrs = [r for r in a['reasons'] if '/heuristic/H4' in r and ': plausible' not in r]
    rows.append(dict(id=os.path.basename(os.path.dirname(f)), T=cl['time_log2'], prep=cl['preprocessing_log2'], prep_share=2 ** (cl['preprocessing_log2'] - cl['time_log2']),
                     form=form, status=a['status'], eligible=a['eligible'], h4_fatal=bool(hrs), reasons_h4=hrs))
for r in rows: print(r['id'], r['T'], r['form'], '%.4f' % r['prep_share'], r['status'], 'H4_FATAL' if r['h4_fatal'] else '')
# the known failing / passing split used as the control for the rule "H4 fatal in a not_evaluable ruling"
fail = [r for r in rows if r['h4_fatal']]; ok = [r for r in rows if r['eligible']]
print('H4-fatal dossiers', len(fail), [r['id'] for r in fail]); print('eligible dossiers', len(ok), [r['id'] for r in ok])
# current package R38M3
P = _hca_public_path_text('__HCA_WORKSPACE__/research/tools/build_pkg/scratch/pkgR38M3/pkg/sha256-r38')
cl = json.load(open(P + '\claim.json', encoding='utf-8')); c = cl['claim']
ids = [h['id'] for h in cl['heuristics']]; h4 = [h for h in cl['heuristics'] if h['id'].startswith('H4')]
T, prep = c['time_log2'], c['preprocessing_log2']
AC = 78; share_ac = 2 ** (AC - T); share_prep = 2 ** (prep - T)
print('R38M3 H4 ids', [h['id'] for h in h4], 'role', [h['role'] for h in h4]); print('A_C share of T %.5f  prep share %.5f  T %.5f' % (share_ac, share_prep, T))
lim = h4[0]['limitations']; print('limitations text:', lim[:200])
N = 789779068018615953003308365799
tot = N
# A_C share exact from the ledger rows (A_C*C = 2^78 x 2728)
exact_share = (2 ** 78 * 2728) / N
print('exact A_C share', exact_share)
# at what A_C would R38M3 reach the 82.8% share of cfeb996a and the 39.3% share of 1393e83b (solve A/(A+rest)=s, rest = N - A_C*C)
rest = N - 2 ** 78 * 2728
for s in (0.2, 0.3934, 0.828):
    A = s / (1 - s) * rest; print('share %.3f needs A_C*C = %.4g -> A_C = 2^%.3f; time_log2 would be %.4f' % (s, A, math.log2(A / 2728), math.log2((A + rest) / 2728)))
# marginal: bits per doubling of A_C at M3
for k in (1, 6):
    n2 = rest + 2 ** (78 + k) * 2728; print('A_C x2^%d: %+.5f bit' % (k, math.log2(n2 / N)))
# the dense characteristic derivation: evidence that the package cites (not in package)
pr = open(P + '\proof.md', encoding='utf-8').read()
print('proof mentions 593,858:', '593,858' in pr, '| job115/2^31.9 metered pair search in package:', ('2^31.9' in pr) or ('job115' in pr))
json.dump(dict(rows=rows, share_ac=share_ac, share_prep=share_prep, exact_share=exact_share), open('g07_judge.json', 'w'), indent=1)
