"""Builds ATLAS_POSEIDON.md from the pinned constants and the fact scripts' outputs. Run: python build_atlas.py"""

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

import sys, os, re, json
sys.path.insert(0, _hca_public_path_text('__HCA_WORKSPACE__/research/poseidon/orchard/impl'))
import poseidon_ref as R
HERE = os.path.dirname(os.path.abspath(__file__))
P, RC, MDS, CAP = R.P, R.RC, R.MDS, R.CAPACITY
M = [list(r) for r in MDS]
def h(x): return '0x%x' % x
def inv(a): return pow(a, P-2, P)
FB = json.load(open(os.path.join(HERE, 'facts_basic.json')))
K = pow((CAP + RC[0][2]) % P, 5, P)
Minv_row2 = FB['Minv_row2']
out = []
def w(s=''): out.append(s)

# ------------------------------------------------------------------ helpers: generic degrees
def seq(r): return [(i, 'full') for i in range(4)] + [(i, 'partial') for i in range(4, 4+r)] + [(i, 'full') for i in range(60, 64)]
def degtab(r):
    d = [1, 1, 0]; t = {}
    for idx, kind in seq(r):
        t[(idx, 'C')] = list(d)
        d = [5*x for x in d] if kind == 'full' else [5*d[0], d[1], d[2]]
        t[(idx, 'S')] = list(d)
        m = max(d); d = [m, m, m]
        t[(idx, 'M')] = list(d)
    return t
T1, T2 = degtab(1), degtab(2)
def ab(d): return [x//5 if x else 0 for x in d]      # degree in (A,B) coordinates for rounds >= 0 after S
def dstr(d): return '[%s]' % ', '.join(str(x) for x in d)

# ------------------------------------------------------------------ trace file
def trace_file():
    lines = []
    for r in (1, 2):
        for (nk, rho) in ((0, 0), (1, 2)):
            lines.append('== r=%d input nk=%d rho=%d  state [nk, rho, 2^65] ==' % (r, nk, rho))
            s = [nk, rho, CAP]
            lines.append('init            ' + ' '.join(h(x) for x in s))
            for idx, kind in seq(r):
                s = [(s[i]+RC[idx][i]) % P for i in range(3)]; lines.append('R%-2d after C       ' % idx + ' '.join(h(x) for x in s))
                s = [pow(s[i], 5, P) if (kind == 'full' or i == 0) else s[i] for i in range(3)]; lines.append('R%-2d after S       ' % idx + ' '.join(h(x) for x in s))
                s = R.mds_apply(s); lines.append('R%-2d after M       ' % idx + ' '.join(h(x) for x in s))
            assert s[0] == R.hash_reduced(nk, rho, r)
            lines.append('output lane 0 = ' + h(s[0])); lines.append('')
    open(os.path.join(HERE, 'TRACE_EXAMPLE.txt'), 'w').write('\n'.join(lines))
trace_file()

# ------------------------------------------------------------------ toy summary from output file
toy_txt = open(os.path.join(HERE, 'facts_toy_output.txt')).read()
toy_rows = {}
cur = None
for line in toy_txt.splitlines():
    m = re.match(r'q=(\d+) \(.*\), r=(\d+)', line)
    if m: cur = (int(m.group(1)), int(m.group(2))); toy_rows[cur] = []; continue
    m = re.match(r'\s+seed (\d+): image size (\d+)/(\d+), fiber mean ([\d.]+) var ([\d.]+) .*?colliding input pairs (\d+) = ([\d.]+) x', line)
    if m and cur: toy_rows[cur].append((float(m.group(4)), float(m.group(5)), float(m.group(7)), int(m.group(2)) == int(m.group(3))))
toy_lines = []
for (q, r), rows in sorted(toy_rows.items()):
    if not rows: continue
    ratios = [x[2] for x in rows]; vm = [x[1]/x[0] for x in rows]
    toy_lines.append('| %d | %d | %d | %s | %.4f - %.4f | %.2f - %.2f |' % (q, r, len(rows), 'all' if all(x[3] for x in rows) else 'NOT all', min(ratios), max(ratios), min(vm), max(vm)))

# ================================================================== DOCUMENT
w('# ATLAS_POSEIDON - the levels of the reduced Orchard Poseidon (learning atlas, skeleton v1)')
w()
w(_hca_public_path_text('Written 2026-10-12 by the atlas agent. Folder: `__HCA_WORKSPACE__/research/poseidon/levels/atlas`. Purpose: **find the levels, learn how each behaves and how they interact. No attack scores are estimated anywhere in this file.**'))
w()
w('This is a new target, so this file is a *skeleton*: every card below has the same fields, the numbers are exact, and every statement carries a label. Where a field is still empty ("not yet looked at") that is a hole to dig, not a verdict.')
w()
w('## 0. How to read this file')
w()
w('Labels on every statement:')
w('- **OBSERVED** - measured by a command in this folder (the script and section are named). Re-run it to reproduce.')
w('- **PROVED** - follows by a short argument that is written out or obvious from the definitions (and, where cheap, also checked numerically).')
w('- **DERIVED** - follows from OBSERVED/PROVED facts by an argument not fully written out here; check before relying on it.')
w('- **GUESS** - an idea or expectation; nothing was run.')
w()
w('Fact scripts (all single-process, exact big-int arithmetic on the pinned constants, read as data; implementation `orchard\\impl\\poseidon_ref.py`, validated 11/11 against public vectors):')
w()
w('| script | what it computes | output file |')
w('|---|---|---|')
w('| `facts_basic.py` | field facts, constants table facts, MDS (Cauchy, minors, char. poly, irreducibility), partial-round difference trails, constants normal form, round-0 plane, special directions | `facts_basic_output.txt`, `facts_basic.json` |')
w('| `facts_extra.py` | powers of M still MDS, Krylov determinants, plane vs trail spaces | `facts_extra_output.txt` |')
w('| `facts_degree.py` | generic degree table, leading-coefficient tracker, exact line polynomials (Kronecker), special directions, exact bivariate monomial counts, forward/reverse Jacobians | `facts_degree_output.txt` |')
w('| `facts_ab.py` | round-0 reparametrisation (A,B) and monomial counts in (A,B) | `facts_ab_output.txt` |')
w('| `facts_toy.py` | toy copies over F_q (q = 257 ... 12289), exhaustive over all q^2 inputs | `facts_toy_output.txt` |')
w('| `build_atlas.py` | assembles this file and `TRACE_EXAMPLE.txt` (state after every step for inputs (0,0) and (1,2)) | |')
w()
w('Notation: `a = nk + c0,0`, `b = rho + c0,1`, `A = a^5`, `B = b^5`, `K = (2^65 + c0,2)^5`, `S` = the S-box layer, `M` = the MDS matrix, `cr,i` = original-round-r constant for lane i, `Pallas p = 0x40000000000000000000000000000000224698fc094cf91b992d30ed00000001`, `F` = F_p. "(nk,rho)-degree" = total degree as a polynomial in the two input elements.')
w()

# ------------------------------------------------------------------ 1 ladder
w('## 1. The levels (what the target is, in order)')
w()
w('State = 3 lanes over F_p, init `[nk, rho, 2^65]` (2^65 = `%s`, a 66-bit number, far below p). A *round* = three steps **C** (add the original round\'s 3 constants) -> **S** (x^5 on all 3 lanes in a full round, on lane 0 only in a partial round) -> **M** (multiply by the fixed 3x3 MDS matrix). Output = lane 0 after the last M. Constants/MDS are the deployed ones (never regenerated for reduced r).' % h(CAP))
w()
w('| original round | kind | level for r=1 | level for r=2 | S-boxes acting |')
w('|---|---|---|---|---|')
rows1 = {idx: pos+1 for pos, (idx, k) in enumerate(seq(1))}
rows2 = {idx: pos+1 for pos, (idx, k) in enumerate(seq(2))}
for idx in list(range(4)) + [4, 5] + list(range(60, 64)):
    kind = 'full' if (idx < 4 or idx >= 60) else 'partial'
    note = '3 (lane 2 of R0 acts on a constant)' if idx == 0 else ('3' if kind == 'full' else '1 (lane 0)')
    w('| R%d | %s | %s | %s | %s |' % (idx, kind, 'L%d' % rows1[idx] if idx in rows1 else 'not run', 'L%d' % rows2[idx] if idx in rows2 else 'not run', note))
w()
w('R5 exists only for r=2, so R60..R63 sit one level later when r=2.')
w()
w('```')
w('r=1:  init -> R0 -> R1 -> R2 -> R3 -> R4(partial) ------------> R60 -> R61 -> R62 -> R63 -> lane 0')
w('r=2:  init -> R0 -> R1 -> R2 -> R3 -> R4(partial) -> R5(partial) -> R60 -> R61 -> R62 -> R63 -> lane 0')
w('        |<-- full block A (4 rounds) -->|<- partial block (r rounds) ->|<-- full block B (4 rounds) -->|')
w('```')
w()
w('Counts (DERIVED from the definition): r=1 has 9 rounds, 25 S-box evaluations (24 on non-constant values: R0 lane 2 acts on the constant 2^65 + c0,2) and 9 MDS applications; r=2 has 10 rounds, 26 S-box evaluations (25 non-constant), 10 MDS. Round 63 needs only row 0 of M (the other 2 outputs are never read).')
w()

# ------------------------------------------------------------------ 2 key structure
w('## 2. Structure that spans several levels (read before the cards)')
w()
w('Each item is a *finding about how levels talk to each other*. IDs (X1..) are referenced from the cards.')
w()
w('**X1 - every round is a bijection of F^3, so distinct inputs never collide in the full state.** [PROVED] C is a translation; S is x -> x^5 on a lane, a bijection because gcd(5, p-1) = 1 (p-1 = 2^32 * 3 * 463 * C212, no factor 5; `facts_basic_output.txt` "gcd(5,p-1)= 1"); M is invertible (det != 0). So the 3-lane map Pi is a bijection and two different inputs give two different final *states*. A collision exists only because the output keeps **lane 0 only**: the two final states agree in lane 0 and differ in lanes 1 and/or 2. [OBSERVED toy] q=257, r=1 and r=2: all 66049 inputs give 66049 distinct 3-lane outputs, while lane 0 alone has only 257 values and the pair (lane0,lane1) has 41757 / 41681 distinct values of 66049 (`facts_toy_output.txt`, "structure checks").')
w()
w('**X2 - round 0 is a reparametrisation of the input domain.** [PROVED] The domain is all of F x F (canonical nk, rho < p). The map (nk, rho) -> (A, B) = ((nk+c0,0)^5, (rho+c0,1)^5) is a bijection of F^2 (translation, then 5th power on each coordinate; inverse x -> x^d with d = 5^-1 mod p-1 = `%s`, 254 bits). Lane 2 enters round 0 as the constant 2^65 + c0,2, so its S-box output is the constant K = `%s`. The state after R0 is therefore `M * (A, B, K)^T`: **an affine plane in F^3**, and (A,B) range over *all* of F^2. Collisions of the hash in (nk,rho) correspond one-to-one to collisions of H(A,B) = (rounds 1..63 applied to M*(A,B,K)). Consequences: (i) the constants c0,0 and c0,1 are pure re-labelling of the input and cannot matter structurally; (ii) in (A,B) the polynomials are one level lower: output degree 5^8 (r=1) / 5^9 (r=2) instead of 5^9 / 5^10. [OBSERVED] `facts_ab.py`: hash_reduced(nk,rho) == H(A,B) on 20 random inputs for each r, and the fifth-root inversion returns (nk,rho); also (M^-1 s)_2 == K for round-0 outputs (`facts_basic.py`).' % (h(pow(5, -1, P-1)), h(K)))
w()
w('**X3 - the plane P0 after round 0 and the difference spaces.** [DERIVED + OBSERVED] Differences between two states of P0 lie in the direction space {d : (M^-1 d)_2 = 0}; its intersection with {d_0 = 0} is one line (spanned by `(0, %s, %s)`, `facts_extra_output.txt`). The r=2 two-round trail vector (see X6) is *not* in that direction space. These statements concern the states right after R0 only.' % (h(int(FB['Minv_row2'][2], 16)), h((-int(FB['Minv_row2'][1], 16)) % P)))
w()
w('**X4 - in the dense block nothing is dropped.** [OBSERVED] In rounds R1..R3 every lane depends on both nk and rho at every step after R0.M, the Jacobian of the 3-lane state w.r.t. (nk,rho) has rank 2 at every step, and every lane influences the output at every point (`facts_degree_output.txt` part F). The only places where "who influences whom" is not complete: before R0.M lane 0 depends only on nk, lane 1 only on rho, lane 2 on nothing; after the last M only lane 0 is read.')
w()
w('**X5 - a partial round has exactly one non-linear scalar.** [PROVED] With w = (s_0 + c_r,0)^5, the partial round is `s\' = M * (w, s_1 + c_r,1, s_2 + c_r,2)^T`: all three output lanes are *affine* in (w, s_1, s_2) with coefficient column M_.,0 on w. So a partial round turns the 3-dim state into the 3 coordinates (w, s_1, s_2) via one 5th power and then re-spreads it with M. Constants of lanes 1 and 2 can be carried through: lanes 1,2 constants of the partial round are equivalent to adding `M*(0, c_r,1, c_r,2)` to the *next* round\'s constants. [OBSERVED] With this normal form (round-60 effective constants for r=1: `%s`, `%s`, `%s`) the hash is reproduced on 40 random inputs (`facts_basic.py`, "normal form").' % tuple(FB['r1_c60_effective']))
w()
w('**X6 - differences that the partial S-box does not see.** [DERIVED + OBSERVED] If two states entering a partial round have equal lane 0, then w is equal and the output difference is `M*(0, d_1, d_2)` - linear, 2 free dimensions (r=1). For r=2 the difference must also have lane 0 equal after the first M: the direction `d = (0, M_0,2, -M_0,1)` (hex in `facts_basic_output.txt`), 1 free dimension. For r >= 3 the observability determinant det[e0; e0 M; e0 M^2] is nonzero (`%s`), so no difference direction survives three partial rounds unseen. These need the *entry state pair* to agree in lane 0 (a condition on the earlier levels, not studied here).' % h(int('ebe164ab9dff92f6f90c296e3b831a7221b9f7429d21e01d7dc2ebf46e8a8ba', 16)))
w()
w('**X7 - the end of the pipeline is a linear form in three 5th powers.** [PROVED] output y = M_0,0 T_0 + M_0,1 T_1 + M_0,2 T_2 with T_j = (t_j)^5 and t = (state after R62.M) + c63. Because x -> x^5 is a bijection, (T_0,T_1,T_2) is free in F^3 and y is one linear equation in it: the set of states before R63.S with a given output y is an affine plane in T-coordinates (2 free dims). Rows 1,2 of the last M are unused.')
w()
w('**X8 - degree grows by the S-box layers only (5 per full round; 5 on lane 0 per partial round, then M re-mixes).** [PROVED upper bound; OBSERVED exact] The (nk,rho)-degree of every lane after round k is 5^(k+1) in the dense block; after a partial round all three lanes have the degree of lane 0. Exact line degrees (leading coefficient != 0, hence the true degree on that line, hence a lower bound for the true total degree, hence equal to the upper bound): output degree 5^9 = 1953125 (r=1), 5^10 = 9765625 (r=2) (`facts_degree_output.txt` part B, two random lines per r, no leading coefficient was zero).')
w()
w('**X9 - the support of the polynomials is *structured*.** [OBSERVED] In (A,B) coordinates the lanes after R1, R2, R3 have the **full triangle** of monomials: 21, 351, 8001 per lane (degrees 5, 25, 125) (`facts_ab_output.txt`). In (nk,rho) coordinates the supports are smaller than the full triangle: R0: 11 monomials (no mixed terms: a pure sum f(nk)+g(rho)); R1: 301 of 351; R2: 7751 of 8001; both counts equal exactly the number of (i,j) with ceil(i/5)+ceil(j/5) <= 5^k (k=1: 5, k=2: 25) (`facts_degree_output.txt` part E; the 7751 match was checked in this session by direct count). Univariate line polynomials show no zero coefficient through R4 (r=1,2), R5 (r=2), R60 (r=1): dense.')
w()
w('**X10 - lane 2 starts constant, and the degree-drop directions are transient.** [OBSERVED + DERIVED] After R0.M the lane polynomials are M_i0 A + M_i1 B + M_i2 K (linear in (A,B); 11 monomials in (nk,rho)). On a line nk = a + u t, rho = b + v t, lane i loses its top degree after R0 exactly when M_i0 u^5 + M_i1 v^5 = 0; because 5 is invertible mod p-1 there is exactly **one** such direction u/v per lane in F_p (three directions, hex in `facts_basic_output.txt`). On such a line lane i has degree 4 after R0, degree 20 before M in R1, and the next M restores degree 25 (`facts_degree_output.txt` part D): nothing persists past one MDS.')
w()
w('**X11 - which rounds can be skipped/merged in thought.** [DERIVED] Constants of lanes 0,1 in R0 are absorbed into the input labelling (X2); constants of lanes 1,2 in partial rounds are absorbed into the next round (X5); rows 1,2 of the last M are dead (X7); lane 2 of R0.S is a constant. Everything else is live.')
w()

w('### Hand-off table: what each level gives to the next')
w()
w('| level | receives | does | hands on |')
w('|---|---|---|---|')
w('| init | (nk, rho) free, 2^65 fixed | - | plane {s_2 = 2^65}, 2 free dims |')
w('| R0 | that plane | translate, 5th power (a bijection of the input), M | affine plane P0 = M*(A,B,K), (A,B) free in F^2 (X2) |')
w('| R1 | P0 | translate, 3 quintics, M | 2-dim surface, (A,B)-degree 5, (nk,rho)-degree 25, full triangle support in (A,B) |')
w('| R2, R3 | surface | same | (A,B)-degree 25, then 125; every lane depends on both inputs |')
w('| R4 (R5) | 3-lane state | one quintic (lane 0) and affine mixing of (w, s_1, s_2) | all 3 lanes at 5x the old maximum degree; differences with d_0 = 0 pass linearly (X6) |')
w('| R60..R62 | state | same as R1..R3 | degree x5 per round |')
w('| R63 | state | quintics, then row 0 of M only | y = linear form of three 5th powers (X7) |')
w('| output | y | - | 32 bytes little endian, top byte <= 0x40 |')
w()

# ------------------------------------------------------------------ 3 global cards
w('## 3. Global cards (objects that every round uses)')
w()
w('### G1 - the field Pallas F_p')
w()
w('- [OBSERVED `facts_basic.py`] p has 255 bits; p mod 4 = 1, p mod 3 = 1, p mod 5 = 2, p mod 8 = 1.')
w('- [OBSERVED] p - 1 = 2^32 * 3 * 463 * C, with C = 4852402207910482324454106387152561316357015077916052529702775169 (212 bits, composite by Miller-Rabin, **not factored** by the small Pollard-rho run used here; factoring it is an open learning item). 2-adicity 32. gcd(5, p-1) = 1.')
w('- [OBSERVED] p + 1 = 2 * 43 * 257 * 25457 * C\', C\' = 51449374779015257336754183746739814209752300176005070023712222882867 (unfactored composite). p^2 + p + 1 = 3 * 73 * 5839 * 12221196943 * 5187662682403 * C\'\' (C\'\' a 412-bit composite, unfactored; C\' is 225 bits).')
w('- [OBSERVED] ord of p mod 5 = 4, so Phi_5(x) is irreducible over F_p: x^5 = 1 has only the root 1 in F_p; the primitive 5th roots of unity live in F_{p^4}. [DERIVED] consequently every element has exactly one 5th root in F_p.')
w('- [OBSERVED] sqrt(-1) = `%s` and its negative `%s`. x^4 = -1 has 4 solutions in F_p (primitive 8th roots), listed in `facts_basic_output.txt`.' % tuple(FB['sqrt_m1']))
w('- [OBSERVED] inverse exponent d = 5^-1 mod (p-1) = `%s` (254 bits).' % h(pow(5, -1, P-1)))
w('- [OBSERVED] order of 5 modulo 2^32 is 2^30, modulo 3 is 3, modulo 463 is 463; the remaining factor C is unfactored, so the cycle-length spectrum of x -> x^5 on F_p^* is only known on the 2-power, 3 and 463 parts.')
w()
w('### G2 - the S-box x -> x^5')
w()
w('- [PROVED] bijection of F_p (gcd(5,p-1)=1). Odd: S(-x) = -S(x). Homogeneous: S(lambda x) = lambda^5 S(x). Hence S(i x) = i S(x) for i = sqrt(-1): S commutes with the 4th roots of unity (the constants break this symmetry in the full cipher; the symmetric constant-free map would be homogeneous).')
w('- [PROVED] fixed points: x^5 = x <=> x^4 = 1 or x = 0, exactly **5**: 0, 1, -1, i, -i (p = 1 mod 4). x^5 = -x has 4 solutions (x^4 = -1). x^5 = 0 only at 0. Derivative 5 x^4 vanishes only at 0 (p != 5). For q = 3 mod 4 (toy q = 4099) only 3 fixed points {0, 1, -1}.')
w('- [PROVED + OBSERVED toy] (x+a)^5 - x^5 = b is a quartic in x; with y = x + a/2 it is even in y (difference of (y+h)^5 and (y-h)^5, h = a/2), so solutions come in +- pairs: at most 4, and exactly one b has 3 solutions (y = 0 plus a pair). Exhaustive toy spectra for a = 1,2,3 are identical (homogeneity): q=257: {0:160, 2:65, 3:1, 4:31}; q=769: {0:480, 2:193, 3:1, 4:95}; q=1009: {0:630, 2:253, 3:1, 4:125}; q=4099: {0:2562, 2:1024, 3:1, 4:512} (`facts_toy_output.txt`).')
w('- [DERIVED] cost of x^5: 3 multiplications (square, square, multiply). Inverse x^(1/5) = x^d, 254-bit exponent.')
w('- Edge values for a lane input a: a = 0 -> output 0 and zero first-order sensitivity; a = +-1, +-i -> S-box acts as the identity; for round 0 the nk (rho) values hitting these are listed in card R0.S.')
w()
w('### G3 - the MDS matrix M (same in all 64 rounds)')
w()
w('```')
for i in range(3): w('row %d: %s' % (i, '  '.join(h(x) for x in M[i])))
w('```')
w()
w('- [OBSERVED `facts_basic.py`] all 9 entries nonzero, all 9 2x2 minors nonzero, det = `0x9729bde00d1e0d80a9ebc3ef5c053f8664f4b7b04c9a6fb6eef310a2567ad8f` != 0: **MDS (branch number 4)** [PROVED by these checks]. M^k is also MDS (all minors nonzero) for k = 1..8 and M^-1 is MDS (`facts_extra_output.txt`). Entries are 251-254 bits (no small entries); none equal; not symmetric; M^2 is not a scalar.')
w('- [OBSERVED] **Cauchy matrix**: with N_ij = 1/M_ij, N_ij - N_i0 - N_0j + N_00 = 0 for all i,j, so M_ij = 1/(x_i + y_j) with x = (0, `%s`, `%s`), y = (`%s`, `%s`, `%s`) (one valid choice; (x,y) -> (x+s, y-s) is the only freedom). The Cauchy determinant formula reproduces det M. The x_i, y_j are not small (251-bit differences).' % (FB['cauchy_x'][1], FB['cauchy_x'][2], FB['cauchy_y'][0], FB['cauchy_y'][1], FB['cauchy_y'][2]))
w('- [OBSERVED] characteristic polynomial x^3 - T x^2 + S x - D with T = `0x2c782b1a7751c9fcb91ccffd2c7f970b64106a45558def37ee97f7c10ccdf481`, S = `0x20812dc43b3c46d1b2de0988f832e18aee5863772acb2cdeea88d819bff12070`, D = det. It is **irreducible over F_p** (x^(p^3) = x mod f, x^p != x mod f): no eigenvalue in F_p, **no 1-dim or 2-dim invariant subspace over F_p**; M generates a copy of F_{p^3}. The order of M divides p^3 - 1 (M^(p^3-1) = I verified) and is not (p^3-1)/q for the known primes q (2, 3, 463, 73, 5839, 12221196943); exact order not determined (cofactors unfactored). det M is a quadratic non-residue; M_0,0 and M_0,1 are non-residues, M_0,2 a residue.')
w('- [OBSERVED] row 0 (the output row): `%s`, `%s`, `%s`. Row 2 of M^-1 (normal of the plane P0): `%s`, `%s`, `%s`.' % (h(M[0][0]), h(M[0][1]), h(M[0][2]), *FB['Minv_row2']))
w('- [OBSERVED] observability/controllability: det[e0; e0 M; e0 M^2] and det[M e0, M^2 e0, M^3 e0] are nonzero (lane 0 is a cyclic vector in both senses).')
w('- Not yet looked at: eigenvectors over F_{p^3}; minimal k with a zero entry in M^k beyond 8; sparse-matrix factorisations M = M\' M\'\' used for partial rounds.')
w()
w('### G4 - the constants table')
w()
w('- [OBSERVED `facts_basic.py`] 64 rounds x 3 lanes = 192 constants, all distinct, none 0, none +-1, none +-i, none a negative of another; bit length 243..254 (only 4 below 250 bits); about half are quadratic residues (90/192); no relation c_i = +-k c_j (k <= 5) inside a round; no equal constant in consecutive rounds; c_(r+1) = M c_r never holds. Smallest |c| (signed) has 243 bits. They look like random field elements (as expected from the Grain-LFSR generation in the halo2 source; not re-derived here).')
w('- [OBSERVED] used rows: R0..R5, R60..R63 are tabulated in the cards below. The source file hash recorded by the organiser: sha256 `b19d4e50867e67af232db34f88d2bf8629d6d7ee2496458a8e37ae758772acd5`.')
w('- [OBSERVED] capacity entry: 2^65 + c0,2 = `%s` (253 bits), whose 5th power is K = `%s`.' % (h((CAP+RC[0][2]) % P), h(K)))
w()

# ------------------------------------------------------------------ 4 cards
w('## 4. Cards, one per round and step')
w()
w('Field list for every card: **reads / writes**, **linear?**, **degree after the step** (per lane, in (nk,rho); in brackets the degree in (A,B) coordinates, X2), **free inputs influencing each lane** (of the 2 inputs nk, rho; measured by Jacobian, `facts_degree.py` F), **untouched lanes**, **special facts**, **what moves when it changes**.')
w()
w('The init state `[nk, rho, 2^65]` is level 0: lanes read: none; writes lane 0 = nk (free), lane 1 = rho (free), lane 2 = 2^65 (fixed). Degrees [1, 1, 0]. Influence: lane 0 {nk}, lane 1 {rho}, lane 2 {}. Jacobian rank 2. Free dimension of the state set: 2 (a plane in F^3: {s_2 = 2^65}).')
w()

def card(idx, rlabel):
    kind = 'full' if (idx < 4 or idx >= 60) else 'partial'
    c = RC[idx]
    w('### %s - %s round' % (rlabel, kind))
    w()
    if idx < 4: pos = 'L%d (r=1 and r=2)' % (idx+1)
    elif idx in (4,): pos = 'L5 (r=1 and r=2)'
    elif idx == 5: pos = 'L6 (r=2 only)'
    else: pos = 'r=1: L%d, r=2: L%d' % (rows1[idx], rows2[idx])
    w('Position: %s. Original round index %d (constants row %d of the table, never regenerated).' % (pos, idx, idx))
    w()
    d1, d2 = T1.get((idx, 'C')), T2.get((idx, 'C'))
    def dd(step):
        a, b = T1.get((idx, step)), T2.get((idx, step))
        def one(d): return dstr(d) + (' [AB n/a: not yet in (A,B)]' if (idx == 0 and step == 'C') else ' [AB ' + dstr(ab(d)) + ']')
        if a is None: return 'r=2: ' + one(b)
        if b is None: return 'r=1: ' + one(a)
        if a == b: return one(a)
        return 'r=1: %s; r=2: %s' % (one(a), one(b))
    w('| step | reads -> writes | linear? | degree after step (nk,rho) | influence {nk,rho} per lane |')
    w('|---|---|---|---|---|')
    if idx == 0:
        infC = 'lane0 {nk}, lane1 {rho}, lane2 {}'
        infS = 'lane0 {nk}, lane1 {rho}, lane2 {}'
        infM = 'all three lanes {nk, rho}'
    else:
        infC = infS = infM = 'all three lanes {nk, rho}'
    w('| C | lanes 0,1,2 -> lanes 0,1,2 (adds the 3 constants below) | affine (translation) | %s | %s |' % (dd('C'), infC))
    if kind == 'full':
        w('| S | each lane read and written independently (x -> x^5, 3 S-boxes) | **no**, 3 quintics | %s | %s |' % (dd('S'), infS))
    else:
        w('| S | lane 0 -> lane 0 (x^5); lanes 1,2 pass unchanged | **no** on lane 0 only | %s | %s |' % (dd('S'), infS))
    w('| M | lanes 0,1,2 -> lanes 0,1,2 (dense MDS, all 9 entries used) | linear | %s | %s |' % (dd('M'), infM))
    w()
    w('Constants (C step): lane 0 `%s` (%d bits), lane 1 `%s` (%d bits), lane 2 `%s` (%d bits).' % (h(c[0]), c[0].bit_length(), h(c[1]), c[1].bit_length(), h(c[2]), c[2].bit_length()))
    w()
    w('Special / boring facts:')
    if idx == 0:
        w('- [PROVED] **C**: adding c0,0 to nk and c0,1 to rho is a re-labelling of the input domain (a bijection of F x F); only lane 2 matters: 2^65 + c0,2 = `%s`. (Constants are not small, not equal, not related - G4.)' % h((CAP+c[2]) % P))
        w('- [PROVED] **S**: lanes 0,1 are the bijections a -> a^5, b -> b^5 of the input; lane 2 is a *constant*, K = `%s`. The S-box on lane 2 carries no freedom. nk values at which the lane-0 S-box input a is a fixed point / zero: a=0: nk = `%s`; a=1: `%s`; a=-1: `%s`; a=i: `%s`; a=-i: `%s` (listed with the rho analogues in `facts_basic_output.txt`). At a=0 the derivative wrt nk is 0 (first-order insensitive point), same for rho at b=0.' % (h(K), h((-c[0]) % P), h((1-c[0]) % P), h((P-1-c[0]) % P), h((int(FB['sqrt_m1'][0], 16)-c[0]) % P), h((int(FB['sqrt_m1'][1], 16)-c[0]) % P)))
        w('- [PROVED] **M**: output = A * M_.,0 + B * M_.,1 + K * M_.,2: the state set is the **affine plane** {s : (M^-1 s)_2 = K} (X2), 2-dimensional, with (A,B) free over F^2. Each lane is a polynomial with exactly 11 monomials in (nk,rho) and no mixed term (OBSERVED), 3 monomials in (A,B).')
        w('- [OBSERVED] degree-drop lines (X10): exactly one direction u/v per lane.')
        w('- What moves when it changes: changing nk by e moves lanes 0,1,2 of the output by e-dependent multiples of the column M_.,0 (via A) - all three lanes move together along one fixed direction (column 0), rho along column 1; nk and rho move the state along two *different fixed directions* (the plane\'s two axes).')
    elif idx in (1, 2, 3):
        extra = {1: '[OBSERVED] after M: 301 monomials per lane in (nk,rho) (of 351 in the full triangle of degree 25), 21 in (A,B) (full triangle of degree 5).',
                 2: '[OBSERVED] after M: 7751 monomials per lane in (nk,rho) (of 8001), 351 in (A,B) (full triangle of degree 25).',
                 3: '[OBSERVED] after M: 8001 monomials per lane in (A,B) (full triangle of degree 125); the (nk,rho) expansion was not enumerated (too large for the dict code); the support law of X9 *predicts* 195001 monomials out of the triangle\'s 196251 for degree 625 - PREDICTION, untested.'}[idx]
        w('- %s' % extra)
        w('- [PROVED] S: all three S-boxes act on non-constant values; each is a bijection; S-box inputs are zero only on a curve per lane (codimension 1): a lane polynomial of (nk,rho)-degree %d vanishing locus.' % T1[(idx, 'C')][0])
        w('- [OBSERVED] no constant relation is visible: all constants of the table are 243-254 bit unrelated values (no zero, +-1, +-i; G4).')
        w('- What moves when it changes: a change in any one input lane of M moves all 3 output lanes (MDS, branch number 4: of the 6 numbers (input difference lanes, output difference lanes) at least 4 are nonzero); S-box: derivative 5x^4 is nonzero except at x = 0.')
    elif idx in (4, 5):
        wch = 'lane 0 constant c_%d,0' % idx
        w('- [PROVED] **S** acts on lane 0 only; lanes 1 and 2 are **untouched by the non-linearity** in this round (they only receive their constants and are mixed by M). After M the state is `M * (w, s_1 + c_%d,1, s_2 + c_%d,2)` with w = (s_0 + c_%d,0)^5 (X5): affine in (w, s_1, s_2).' % (idx, idx, idx))
        w('- [PROVED] **constants of lanes 1,2 carried forward**: M*(0, c_%d,1, c_%d,2) = (%s, %s, %s) is added to the next round\'s constants (X5; verified on 40 inputs).' % (idx, idx, *[h(sum(M[i][j]*[0, c[1], c[2]][j] for j in range(3)) % P) for i in range(3)]))
        w('- [DERIVED] degree: lane 0 of the S-box output has degree 5 x (degree of the incoming lane 0); lanes 1,2 keep the incoming degree; after M all three lanes have the new maximum (dense M, no cancellation seen on random lines: leading coefficient nonzero, `facts_degree.py` B).')
        w('- [DERIVED] differences that avoid the S-box: X6. The S-box of R4 sees no difference iff the incoming difference d has d_0 = 0; for r=2 the S-box of R5 sees none iff additionally (M d)_0 = 0.')
        w('- What moves when it changes: only the lane-0 value s_0 moves w non-linearly; a change confined to lanes 1,2 changes the output linearly (M*(0,d_1,d_2)) with w unchanged.')
        if idx == 4:
            w('- Next level: r=1 -> R60 (adds c60 + M*(0,c4,1,c4,2)); r=2 -> R5.')
        if idx == 5:
            w('- Only exists for r=2. Reads the state after R4.M, whose lanes are affine in (w4, s_1, s_2).')
    else:
        w('- [PROVED] full round: 3 independent bijective S-boxes then dense M; same card as R1..R3 structurally.')
        if idx == 60:
            w('- [DERIVED] first full round after the partial block: its three input lanes are affine in the partial block\'s scalars (w, s_1, s_2) (X5); w has 5x the (nk,rho)-degree of R3\'s lanes, s_1 and s_2 keep R3\'s degree.')
        if idx == 63:
            w('- [PROVED] only **row 0** of M is used (X7): output y = M_0,0 T_0 + M_0,1 T_1 + M_0,2 T_2 with T = S(state + c63); the two other output lanes are dead (no influence on the result; `facts_degree.py` F reverse-mode: after the last M only lane 0 has a nonzero gradient).')
            w('- [DERIVED] output encoding: lane 0 as a canonical 32-byte little-endian integer < p (< 2^254.x); the top byte is therefore <= 0x40.')
            w('- The degrees in the table for lanes 1,2 after this M are formal: those lanes are dead. What moves when it changes: a change of one S-box output T_j moves the output by M_0,j times that change (one multiplication) and nothing else.')
        else:
            w('- What moves when it changes: every lane input affects all 3 outputs of M; every lane after this M influences the final output (reverse-mode gradient nonzero on all 3 lanes; OBSERVED, `facts_degree.py` F).')
    w()

for idx in (0, 1, 2, 3, 4, 5, 60, 61, 62, 63):
    card(idx, 'R%d' % idx)

w('### Output O - lane 0 of the final state')
w()
w('Reads lane 0 after R63.M; writes the digest (canonical 32 bytes little endian). Linear form of three 5th powers (X7). Degree: 5^9 (r=1), 5^10 (r=2) in (nk,rho); 5^8, 5^9 in (A,B). The map (nk,rho) -> y goes from ~2^510 inputs to ~2^254 outputs, so every output value has about p preimages (2-dim -> 1-dim: a curve of (nk,rho) points per y) [DERIVED; toy: image size = q for every toy and fibre sizes close to q, see section 6].')
w()
w('Backward freedom [DERIVED]: for a fixed y the set of final 3-lane states is the plane {lane 0 = y} (two free lanes); pulling it back through the bijective rounds gives a 2-dim surface in the state space at every level, while the forward set from the input is another 2-dim surface; two surfaces in F^3 meet in a curve, which is the preimage curve of y. Backward steps need 5th roots (exponent d).')
w()

# ------------------------------------------------------------------ 5 tables
w('## 5. Summary tables (generic degrees, r = 1 and r = 2)')
w()
w('Generic degree = what the structure allows (dense M); the exact tracker confirmed no cancellation on random lines (X8). Format: lane degrees (lane 0, lane 1, lane 2) after the step, total degree in (nk,rho).')
w()
for r, T in ((1, T1), (2, T2)):
    w('**r = %d**' % r)
    w()
    w('| round | after C | after S | after M |')
    w('|---|---|---|---|')
    w('| init | [1, 1, 0] | - | - |')
    for idx, kind in seq(r):
        w('| R%d (%s) | %s | %s | %s |' % (idx, kind, dstr(T[(idx, 'C')]), dstr(T[(idx, 'S')]), dstr(T[(idx, 'M')])))
    w()
w('Influence/freedom table [OBSERVED, forward-mode Jacobian at a random point, `facts_degree_output.txt` F]: init through R0.S: lane 0 {nk}, lane 1 {rho}, lane 2 {}; from R0.M to the output every lane depends on both nk and rho; Jacobian rank 2 at every one of the 28 (r=1) / 31 (r=2) recorded points. Reverse: every lane influences the output at every point except after R63.M (only lane 0).')
w()

# ------------------------------------------------------------------ 6 toy
w('## 6. Toy copies')
w()
w('Same structure over F_q with gcd(5, q-1) = 1: 3 lanes, x^5, rounds {0-3 full, r partial, 60-63 full}, init [nk, rho, 2^65 mod q], random Cauchy MDS, random constants, seeds recorded. All q^2 inputs enumerated (`facts_toy.py`). Admissible q: 257 (2-adicity 8), 769 (8), 1009 (4), 4099 (1, q = 3 mod 4), 12289 (12), 65537 (16, too many inputs to enumerate: 4.3e9), 1000003 (prime, gcd(5,1000002) = 1, 2-adicity 1; q^2 = 1e12 too large to enumerate, usable for sampling only). The real p has 2-adicity 32.')
w()
w('Output-fibre statistics of lane 0 (every output value = one fibre) over all inputs, ratios taken against a uniformly random function from q^2 inputs to q outputs [OBSERVED]:')
w()
w('| q | r | seeds | image covers all q values | colliding input pairs / random expectation (min-max) | fibre variance / mean (Poisson = 1; min-max) |')
w('|---|---|---|---|---|---|')
for l in toy_lines: w(l)
w()
w('- [OBSERVED] At toy scale the output fibres look like those of a random function (variance about equal to mean, collision-pair ratio 1.000 +- 0.001): no visible structure at fibre-count level, for any r in 0..3 and any 2-adicity. The structure that *is* certain is X1 (injective on full states) and X2 (round 0 plane), both verified on q=257: all 66049 round-0 outputs lie on the plane (M^-1 s)_2 = K and are distinct.')
w('- [OBSERVED] x -> x^5 on toy fields: 5 fixed points when q = 1 mod 4 (257, 769, 1009), 3 when q = 3 mod 4 (4099); cycle structure: for q = 257 cycle lengths 1,2,4,...,64 (powers of 2), for 1009 lengths 1,2,4,6,12; for 4099 lengths 1,2,682.')
w('- [GUESS] Toy "algebraic degree" saturates (each variable degree <= q-1 after reduction mod x^q - x), so degree statements do not transfer to toys; toys are for fibre/bijection/trail structure, not for degree.')
w('- Not yet done in the toy: reproducing the X6 difference trails by enumeration; restricting to the pairs whose R3-output lane 0 agree; measuring where the partial-round count r starts to matter.')
w()

# ------------------------------------------------------------------ 7 units
w('## 7. Units for learners (one natural group each, 5-10 concrete questions)')
w()
w('Rule for every unit: answer with a command and a label (OBSERVED / PROVED / DERIVED / GUESS); record empty squares too. Use `poseidon_ref.py`, constants as data, toy fields for enumerations. No score estimates.')
w()
units = [
 ('U1 - Input and round 0 (init, R0.C, R0.S, R0.M)', [
  'Verify X2 on the real field for 1000 random inputs and on toys exhaustively: is (nk,rho) -> (A,B) a bijection and is H(A,B) = hash? (done on 20 inputs; extend and record the failure count = 0).',
  'The plane P0 = {(M^-1 s)_2 = K}: give its equation with full numbers; list the two axis directions (M columns 0 and 1) and the value K. Does K depend on the 2^65 entry in any other way? Redo with capacity values 0, 1, a fixed point, to see which parts of the structure change.',
  'Do the constants c0,0 and c0,1 matter at all? On toys, change them and compare the complete fibre multisets: identical (expected) or not?',
  'The nk values at which a = nk + c0,0 is 0, +-1, +-i: S-box acts as 0 or identity. Compute the same for rho and the lane-2 value 2^65 + c0,2, and list which are in canonical range (all are).',
  'The three degree-drop directions (X10): confirm exactly one direction per lane on toys by brute force over all (u:v), q+1 directions, for several seeds.',
  'Cost and structure of the inverse: compute x^(1/5) for 100 random values by x^d and count squarings/multiplications for d (254-bit, Hamming weight?). Is there a shorter addition chain?',
  'What happens at the 5 fixed points of the S-box for both nk and rho simultaneously (25 input pairs): does the state after R0 look special (small coordinates, collinear)?',
  'Is there any input on the plane P0 whose image after R1.C has a zero coordinate for 2 lanes at once? (Solve for the intersection of two curves.)'
 ]),
 ('U2 - Rounds 1-3 (the dense block)', [
  'Reproduce the monomial counts of X9 for R1, R2 and extend to R3 in (nk,rho): does the law "ceil(i/5)+ceil(j/5) <= 5^k" hold for k = 3 (the prediction is a number; compute it first, then enumerate if feasible)?',
  'In (A,B) coordinates the supports are full triangles. Is any coefficient pattern visible (e.g. the top homogeneous form of a lane after R1, R2: factor it over F_p; how many linear factors?). The top form after R0 is M_i0 X^5 + M_i1 Y^5 with exactly one linear factor over F_p (Phi_5 irreducible, X10).',
  'What is the degree of the implicit equation of the surface S_k = image of the plane after round k (k = 1,2)? Measure on toy q=257: find the least degree d such that a nonzero polynomial of degree <= d in 3 variables vanishes on all 66049 points (linear algebra over F_q).',
  'Zero-sensitivity set: the S-box derivative 5x^4 vanishes only at 0. For R1 the locus {lane i input = 0} is a curve per lane; how many points does it have on toy q = 257, 769 (compare with q), and do the three curves meet?',
  'Special lines (X10): follow the three degree-drop lines through R1 on the real field, then examine whether any *other* lines (e.g. where two lanes drop simultaneously, or lines through the fixed-point set) keep a lower degree for longer. Record every line family checked, including empty ones.',
  'Dependency: for the real hash, which of the 3 lanes after R2.M have an exactly known *affine relation* with lanes of R1? (None expected; verify by interpolation over a small grid on the toy.)',
  'Check the leading-coefficient tracker against exact line polynomials for R1..R3 on 20 random lines; record any line where a coefficient of the exact polynomial is zero (boring but possibly telling).',
  'How does the sum of the (nk,rho)-degree and the number of S-boxes compare with the number of multiplications of one evaluation (X-counts in section 1)? Record the table.'
 ]),
 ('U3 - Partial rounds (R4, and R5 for r=2)', [
  'Verify X5 exactly: the state after R4 equals M*(w, s_1 + c4,1, s_2 + c4,2) with w = (s_0 + c4,0)^5, for 1000 random inputs, and the carried-constant version (done on 40).',
  'Compute the difference spaces of X6 on the real field: for r=1 the 2-dim space {d_0 = 0}, for r=2 the line d = (0, M_0,2, -M_0,1). Take two states with equal lane 0 (construct one by hand, not from the hash) and push them through R4 (and R5): confirm the output difference is M(0,d_1,d_2) (and, for r=2, that the second S-box also sees equal input when d is the trail vector).',
  'How constrained is the set of (nk,rho) pairs whose R3 outputs agree in lane 0? It is a curve in the pair space (equation lane0_R3(x) equals lane0_R3(x2)); what are its degrees? Measure the structure on the toy (q = 257: count pairs, compare with q^2*(q^2-1)/(2q)).',
  'For r = 3: confirm that no difference direction survives (det != 0) and find the largest r for which a direction survives at all (generic bound: 3 - r, the cyclic-vector property).',
  'Sparse form: M = M\' M\'\' with M\'\' having a sparse first row/col (the Poseidon "equivalent partial round" form). Does it exist for this M? Count multiplications saved for r=1 and r=2; check against the reference.',
  'The effective constants (X5): compute them for r=1 and r=2 and confirm that nothing in them is special (small, zero, or equal to a lane-0 constant). Which of the carried constants hits lane 0 of R5 / R60?',
  'Toy: what happens to fibre statistics when r is 0 vs 1 vs 2 vs 3? At q = 257 nothing is visible; test the quantity that does depend on r - e.g. the number of input pairs with equal lane 0 after R3 for which the full outputs also have equal lane 0.',
  'Dead computation: in a partial round only lane 0 enters the S-box. Which arithmetic of R4 is really needed for lane 1,2 outputs? (Count multiplications of the minimal evaluation.)'
 ]),
 ('U4 - Rounds 60-63 and output', [
  'Verify X7 on 1000 inputs: y = sum_j M_0,j * T_j with T = S(state after R62 + c63).',
  'Backward map: given y, pick (T_0, T_1) freely, solve T_2 from the linear equation, compute t_j = T_j^d, then subtract c63 to get the state after R62.M and apply M^-1 to get the S-box outputs of R62. Run it and confirm the forward evaluation returns y. Count the 5th-root exponentiations per backward round.',
  'Degree of the last four rounds as a map of the three-lane state at R60 entry: predicted 5^4 = 625 in lane 0 (since the output depends on 3 variables with degree 5 per round). Verify with exact line polynomials on random lines through state space.',
  'Which values of the lane inputs of R63.S are special (0, +-1, +-i)? A zero input kills a term in the linear form of X7 (two-term form). Are there pairs of outputs of R62.M that make y a function of fewer than 3 fifth powers?',
  'Output encoding: confirm the top byte of the 32-byte output is <= 0x40 for 10^5 random inputs; record the empirical distribution of the top two bits.',
  'r = 1 vs r = 2 at the end: the constants of R60..R63 are the same table rows; what changes is only the incoming state. Verify numerically that rounds 60..63 are literally the same functions in both cases.',
  'Rows 1,2 of R63.M are dead: confirm by changing them (a modified M with other rows) that the hash does not change. Which other dead computations exist (R0.S lane 2 is a constant)?',
  'Reverse-mode influence: confirm for 100 random points that after R62.M all three lanes have nonzero gradient and after R63.M only lane 0.'
 ]),
 ('U5 - The MDS matrix', [
  'Find the eigenvalues of M in F_{p^3}: represent F_{p^3} = F_p[x]/(charpoly) and give the eigenvector(s); is M diagonalisable over F_{p^3} (distinct roots)? Record the three conjugate eigenvalues and their norm (= det) and trace.',
  'Determine the multiplicative order of M: needs the factorisation of p^3 - 1. Which prime factors of it are known (2, 3, 463, 73, 5839, ...)? Try to factor the 212-bit cofactor of p-1 (ECM) and the cofactors of p^2+p+1; compute the exact order or bound it.',
  'Powers: is M^k MDS for all k up to 1000? Find the first k (if any) at which a zero entry or a zero 2x2 minor appears. (k <= 8: none.)',
  'Write down the Cauchy parameters x_i, y_j (X in G3). Are x_i - x_j, y_i - y_j related to each other, to the constants, or to small numbers? Search small integer combinations.',
  'Which vectors v give M v with a zero entry? For each lane i this is a plane; compute the planes, and the intersections of those with the trail line of X6.',
  'The plane P0 normal n = row 2 of M^-1: in which entries is n small or related to M? Compute the ratio n_0 : n_1 : n_2 and compare with M\'s columns.',
  'Is M conjugate (similar) to a companion matrix with a known simple form? Compute a basis in which M acts as multiplication by alpha in F_{p^3} and express lane 0, the capacity direction e2 and the output row e0 in it.',
  'Check whether the matrix has any structure with respect to the squares/non-squares of its entries (the Legendre pattern was recorded in G3); is it random-looking relative to an ensemble of random Cauchy matrices over F_p (draw 1000, compare)?'
 ]),
 ('U6 - The constants table', [
  'Re-derive all 192 constants (and the Cauchy parameters) from the halo2 / Poseidon reference generation (Grain LFSR, field size 255, t=3, R_F=8, R_P=56, alpha=5) and compare with the pinned JSON: do they match exactly? (No generator was run here; this would confirm there is no hidden structure.)',
  'Search for linear relations over small integers among constants of the used rounds (R0..R5, R60..R63) and the MDS entries: use lattice reduction on a 10-20 element subset; record empty results.',
  'Bit-length and high-bit statistics: 243..254 bits recorded; check the distribution of the top byte against uniform on [0, 0x40) (a chi-square on 192 values).',
  'The effective constants after carrying (X5): list them for r=1 and r=2 and run the same relation search on them.',
  'Does c0,2 + 2^65 have any special property (is it a square, a 5th power residue in some subgroup, near a fixed point)? Record Legendre symbols of all used constants.',
  'Are there pairs of rounds whose constant vectors are related by M (c_s = M c_r) or by a scalar? (Checked: consecutive rounds and the relation c_(r+1) = M c_r; extend to all 64*63 pairs.)'
 ]),
 ('U7 - The S-box x^5 on Pallas', [
  'Factor the 212-bit cofactor C of p - 1 (and test its primality certificate) to settle the cycle structure of x -> x^5 on all of F_p^*; list cycle lengths on the 2-power part (2^30), 3 and 463 parts already known.',
  'Differential spectrum on the real field: confirm by sampling that for a != 0 and random b the number of solutions of (x+a)^5 - x^5 = b is 0, 2 or 4 (exactly one b has 3 solutions; the +-pair structure of G2). Record how many b have 0/2/4 solutions on the toys and extrapolate with a formula.',
  'The quartic (x+a)^5 - x^5 - b: write it as a quadratic in y^2 and give the discriminant condition; which b yield 4 solutions in F_p (a quadratic character condition)?',
  'Check symmetries: S(i x) = i S(x), S(-x) = -S(x) (G2). Construct a state/pair of states related by multiplication by i and push it through R0 (where constants break the symmetry): measure what survives.',
  'Fixed points (0, +-1, +-i) and the 4 solutions of x^4 = -1: list them with values; what do the S-box outputs look like for lane inputs in the set {0, +-1, +-i}^3 (125 triples) through an MDS (do any outputs fall in the set again)?',
  'The linear structure of x^5: derivative 5x^4, second derivative 20 x^3, ... Provide the algebraic normal form over F_p and its degree profile under composition with M (X8).',
  'Cost: x^5 = 3 multiplications; x^d = ? multiplications. Compare forward and backward cost per S-box level.',
  'Edge: what is the probability (over random inputs) that some lane value entering an S-box is 0 or a fixed point? Predict (a count of 25 S-box inputs times 5/p) and check on the toys where it is measurable.'
 ]),
 ('U8 - The field and its subgroups (Pallas p)', [
  'Record p - 1, p + 1 and p^2 + p + 1 factorisations as far as they go; what is the smallest unfactored cofactor size? Use ECM/trial division to extend and note the largest prime factor found.',
  'Compute the discrete structure relevant to x^5: the 2-adic tower (2^32 | p-1), elements of order 4 (+-i), order 8 (the four roots of x^4 = -1), order 16, ...; give their values for the first few levels.',
  'F_{p^4} contains the primitive 5th roots of unity (ord_5(p) = 4). Describe the factorisation of x^5 - c over F_p for non-5th-power c (none exist in F_p: every element is a 5th power, so x^5 - c always has exactly one root).',
  'The Cauchy parameters of M and the constants live in F_p; are any of them quadratic residues, 4th powers, 8th powers (use the 2-adic tower)? Record the pattern.',
  'The field F_{p^3} used by M\'s characteristic polynomial: give a degree-3 irreducible polynomial and the Frobenius action on its roots.'
 ]),
 ('U9 - Degrees and polynomial support (the algebraic shape of the whole map)', [
  'Confirm the output degree 5^9 / 5^10 on ten more random lines per r with the leading-coefficient tracker; record any zero leading coefficient (none seen in 4 trials).',
  'In (A,B) coordinates the output has degree 5^8 / 5^9 with the full triangle at rounds 1-3. Is the full-triangle property true at every later round (checked up to R3 only)? Think about why it should (or not) at R4.',
  'Per-variable degree: the degree in nk alone (rho fixed) equals the total degree. Check with exact bivariate arithmetic for R1 and R2 (`facts_degree_output.txt` part E lists deg_nk = deg_rho = 25 and 125).',
  'Count the monomials of the final polynomial as a function of the degree law (conjecture: the (nk,rho) support at round k is {ceil(i/5)+ceil(j/5) <= 5^k}); can you prove it from X2 (a polynomial in A = a^5, B = b^5 expanded in nk, rho)?',
  'The top homogeneous form of the output in (nk,rho): factor it over F_p (R0 gives a quintic form M_i0 X^5 + M_i1 Y^5 with one linear factor). Where are its zeros on the projective line?',
  'Univariate lines: do exact line polynomials of degree 15625 (r=1 after R60) and 78125 (needs longer runs) have any zero coefficient? Record the minimum of the absolute fraction of zeros.',
  'The Jacobian of (nk,rho) -> state has rank 2 everywhere checked; find points where the rank drops to 1 (solve the determinant conditions at R0: a = 0 or b = 0, where a derivative vanishes) and see how far they propagate.',
  'Compare the lane degrees with the S-box count (section 1) and with the number of field multiplications of one evaluation (record: S-boxes cost 3 mults each, M costs 9 each).'
 ]),
 ('U10 - Toy copies', [
  'Rebuild the toy for q = 1,000,003 (gcd(5, q-1) = 1 holds) and repeat X2 (the plane), X5 (carry-forward constants), X7 (the final linear form) by sampling; record the checks that pass.',
  'Run the toys with a *non-Cauchy* random MDS matrix of the same shape (all minors nonzero) and compare fibre statistics and trail dimensions: is Cauchy structure ever visible?',
  'q with high 2-adicity (257, 769, 12289, 65537) versus low (1009, 4099, 1000003): measure the number of fixed points of the S-box layer (triples in {0,+-1,+-i}^3) and any difference in fibre statistics.',
  'Choose capacity values other than 2^65 mod q (0, 1, -1, a fixed point, random) and measure whether the fibre statistics change; the real capacity is a specific number, but in toys we can scan all q values.',
  'Count toy collisions that are "trivial" (related by a symmetry, e.g. multiplication by i when constants vanish) vs generic: set all constants to zero and see whether the fibres change structure.',
  'Measure the number of toy input pairs whose full 3-lane outputs agree in lane 0 *and* lane 1 (X1: they never agree in all three). Compare with the random-function expectation q^4 / (2 q^2).',
  'Make a toy where gcd(5, q-1) = 5 (q = 11, 31, 41, ...) and verify that the bijection property (X1) fails: how many pairs now collide in the full state? This shows the role of the exponent condition.'
 ]),
 ('U11 - What a collision means here (the bijection and the truncation)', [
  'State the exact definition: two distinct canonical (nk,rho) with equal lane 0 after the last M. List which equalities are impossible (equal full state, X1) and which are required (equal lane 0, differing lanes 1,2).',
  'Count: the preimage set of one output value is a 1-dimensional set of F^2 points; for the toy compute the preimage set sizes (fibres) and check that distinct fibre elements always differ in the final lanes 1,2.',
  'Pair view: define D = (state difference at each level). D is never 0 at any level (bijections). At which level is the first lane-0 difference allowed to be 0, and what does a zero lane-0 difference at level k imply for the next S-box (it removes the non-linearity in partial rounds, X6, but not in full rounds)?',
  'Partial collisions: how many (nk,rho) pairs agree in lane 0 after R3.M? Compare with q^2 pairs / q for toys (collision ratio) - record both for r=1 and r=2 (the same for the first 4 rounds).',
  'What does the tail (R60..R63) do to a pair with equal lane 0 but different lanes 1,2? Follow a toy pair through the four rounds and record how the differences grow.',
  'List all structural reductions that exist without computing any attack: X2 (input relabelled), X5 (constant carry), X7 (output linear form), dead M rows. Which level boundaries are "free"?'
 ]),
 ('U12 - r = 1 versus r = 2 and how the levels interact', [
  'Write the exact difference between the two targets: one more partial round R5 inserted between R4 and R60 (R60..R63 and R0..R4 are identical functions). Verify numerically that hash_reduced(.,.,2) = rounds 60..63 applied after R5 after hash_reduced-up-to-R4.',
  'Compare the (nk,rho)-degree sequences: r=1 ends at 5^9, r=2 at 5^10; the extra factor 5 comes entirely from one lane-0 S-box (X5, X8). Verify with the lc tracker.',
  'The difference-trail dimension drops from 2 (r=1) to 1 (r=2) and 0 (r>=3): record it with the explicit vectors and confirm by brute force on toys that no pair of states with equal lane 0 stays equal in lane 0 after two partial rounds unless the difference is along the trail vector.',
  'List what each level hands to the next: R0 -> a plane (2 free dims); R1..R3 -> a 2-dim surface of growing degree; R4 -> a scalar w plus affine mixing; R60..R63 -> bijections ending in a linear form. Draw the ladder with these labels and check each arrow with a command.',
  'Which levels can be inverted cheaply (affine steps: C, M) and which need 5th roots (S)? Count 5th-root exponentiations for walking from the output back to R0.M for r = 1 and r = 2.',
  'Record every statement in this atlas that is only OBSERVED on random samples and write the exhaustive/proof version where possible (the "boring details" audit).'
 ]),
]
for title, qs in units:
    w('### %s' % title)
    w()
    for i, q in enumerate(qs, 1): w('%d. %s' % (i, q))
    w()

# ------------------------------------------------------------------ 8 holes
w('## 8. What is not yet looked at (holes in the atlas)')
w()
w('- Eigenvectors of M over F_{p^3}; exact multiplicative order of M; factorisation of the three unfactored cofactors (p-1, p+1, p^2+p+1).')
w('- Whether the constants really come from the Grain LFSR (not re-derived); relation search among constants (only small-integer relations inside a round and consecutive-round relations were tested).')
w('- Full-triangle behaviour of the (A,B) supports beyond R3, and the (nk,rho) support law beyond R2 (R3: 125 triangle too large for the dict code).')
w('- Difference-trail experiments (X6) on the real field; the sparse equivalent-partial-round form of M.')
w('- Toy experiments restricted to the structure (not just fibre counts): pairs with equal lane 0 after R3, trails, symmetry with zero constants.')
w('- Exact line-degree verification for rounds beyond R60 (r=1) / R5 (r=2) was skipped (cost of multiplying polynomials of degree 78125+); the leading-coefficient tracker covers all rounds.')
w('- Statements about "no relations" in constants are for small parameters only; absence of a hit is not a proof.')
w()
w('## 9. Files')
w()
w('`ATLAS_POSEIDON.md` (this file), `TRACE_EXAMPLE.txt` (state after every step for (nk,rho) = (0,0) and (1,2), r = 1 and 2), the fact scripts and their outputs listed in section 0.')
open(os.path.join(HERE, 'ATLAS_POSEIDON.md'), 'w', encoding='utf-8').write('\n'.join(out) + '\n')
print('written', len(out), 'lines')
