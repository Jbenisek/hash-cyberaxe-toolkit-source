# Non-decomposition witnesses for the r=1 Orchard line polynomial F_j (deg 5^7), j=0,1,2, inner degree m in 5^1..5^6.
# Usage: python make_witnesses.py "0,1,2" "5,25,125"   (j list, m list)
# Reuses levels/decomp/decomp.py (line model, from_poly, B_from_top) exactly as decomp_625_3125.py / decomp_15625.py do.
# Method: H = B_from_top(from_poly(F,m), n, m)  (monic, H(0)=0, deg m; unique in tame case p>n).
#         F = sum c_i H^i with deg c_i < m (H-adic digits, divide and conquer, same recursion as decomp.digits but index-tracked).
#         F = G(H) for some G  <=>  every c_i is constant.  We store the lowest-index nonconstant c_i.

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

import sys, time, json, hashlib, os
sys.path.insert(0,_hca_public_path_text('__HCA_WORKSPACE__/research/poseidon/levels/decomp'))
from decomp import *
OUT = os.path.dirname(os.path.abspath(__file__))
EXPECT = {5:15624, 25:3121, 125:624, 625:124, 3125:24, 15625:4}   # nonconstant-digit counts recorded in RESULT.md / decomp_625_3125.md / d15625.log

def indexed_digits(F, B):
    d = B.degree(); pw = [B]
    while pw[-1].degree()*2 <= F.degree(): pw.append(pw[-1]*pw[-1])
    st = {'nc':0, 'tot':0, 'first':None}
    def rec(G, k, off):
        if G.degree() < 0: return
        if k < 0:
            st['tot'] += 1
            if G.degree() > 0:
                st['nc'] += 1
                if st['first'] is None or off < st['first'][0]: st['first'] = (off, G)
            return
        q, rm = divmod(G, pw[k]); rec(rm, k-1, off); rec(q, k-1, off + (1 << k))
    rec(F, len(pw)-1, 0)
    return st

def coeffs(poly): return [int(x) for x in poly.coeffs()]
def hexlist(cs): return '\n'.join('%064x' % c for c in cs) + '\n'
def sha(s): return hashlib.sha256(s.encode()).hexdigest()

js = [int(x) for x in sys.argv[1].split(',')]; ms = [int(x) for x in sys.argv[2].split(',')]
n = 5**7
for j in js:
    L = Line(j); F = circuit(s0_line(L), 1); assert F.degree() == n
    for m in ms:
        t0 = time.time()
        top = from_poly(F, m); H = B_from_top(top, n, m)
        t1 = time.time()
        assert H.degree() == m and int(H.coeffs()[-1]) == 1 and int(H.coeffs()[0]) == 0
        st = indexed_digits(F, H)
        t2 = time.time()
        assert st['nc'] == EXPECT[m], (j, m, st['nc'])
        idx, G = st['first']; Gc = coeffs(G); Hc = coeffs(H)
        # independent verification: sequential H-adic peeling idx+1 times, compare digit with stored one
        verified = None
        if idx <= 50:
            cur = F
            for _ in range(idx): cur = divmod(cur, H)[0]
            dig = divmod(cur, H)[1]
            verified = (coeffs(dig) == Gc)
        t3 = time.time()
        Hh, Gh = hexlist(Hc), hexlist(Gc)
        name = 'nd_j%d_m%d' % (j, m)
        rec = {'j': j, 'inner_degree_m': m, 'F_degree': n, 'field': hex(p), 'model': 'levels/decomp/decomp.py Line(j) circuit(s0_line(L),1); r=1',
               'H': 'monic, H(0)=0, degree m, coefficient list ascending (c0..cm), 64-hex per coefficient',
               'H_sha256_of_hexlist': sha(Hh), 'nonconstant_digit_index': idx, 'digit_degree': G.degree(),
               'digit_constant_term_hex': '%064x' % Gc[0], 'digit_sha256_of_hexlist': sha(Gh),
               'nonconstant_digit_count': st['nc'], 'digits_visited': st['tot'],
               'meaning': 'F = sum_i c_i H^i with deg c_i < m; c_idx is nonconstant, so F is not G(H) for any G',
               'independent_peel_verification': verified,
               'runtime_s': {'H_candidate': round(t1-t0,1), 'digit_expansion': round(t2-t1,1), 'verify': round(t3-t2,1), 'total': round(t3-t0,1)}}
        if m <= 625:
            rec['H_coeffs_hex'] = Hh.split(); rec['digit_coeffs_hex'] = Gh.split()
        else:
            open(os.path.join(OUT, name + '_H.hex'), 'w').write(Hh)
            open(os.path.join(OUT, name + '_digit.hex'), 'w').write(Gh)
            rec['H_file'] = name + '_H.hex'; rec['digit_file'] = name + '_digit.hex'
        json.dump(rec, open(os.path.join(OUT, name + '.json'), 'w'), indent=1)
        print('j', j, 'm', m, 'digit idx', idx, 'deg', G.degree(), 'nc', st['nc'], 'verified', verified, rec['runtime_s'], flush=True)
