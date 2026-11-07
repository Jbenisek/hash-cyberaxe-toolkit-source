"""Step 2b (GPU): top-degree cube sums of the 6-round digest and of its internal difference on the symmetric
1-round-affine space U<p> (and others), dims beyond CPU reach (up to 33). Kernel: cube6.cu via WSL (run_gpu.sh).
First verifies the kernel against the numpy cube sums (cube_degree.points + organizer round) on small cubes.
Usage: python gpu_cube.py SEED NCUBES SPACES(comma) DIMS(comma) [verify]"""

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

import sys, json, time, random, subprocess
import numpy as np
import symlib as S

seed, ncub = int(sys.argv[1]), int(sys.argv[2])
spaces = sys.argv[3].split(',')
dims = [int(x) for x in sys.argv[4].split(',')]
verify = len(sys.argv) > 5 and sys.argv[5] == 'verify'
rng = random.Random(seed)
FO = json.load(open('fields_out.json'))
MASK = S.MASK
WSLDIR = _hca_public_path_text('__HCA_WORKSPACE__/research/newpaths/untried/s3-deg-idiff')


def space(tag):
    kind, p = (tag[:2], int(tag[2:])) if tag.startswith('Vn') else (tag[0], int(tag[1:]))
    sym = S.sym_basis(p)
    if kind == 'U':
        return p, S.lane16_for(p), sym, sym
    key = f'p{p}_' + ('native_l16' if kind == 'Vn' else 'periodic_l16')
    return p, (S.NATIVE if kind == 'Vn' else S.lane16_for(p)), [int(h, 16) for h in FO['bases'][key]], sym


def rotp(v, p):
    return ((v << p) | (v >> (64 - p))) & MASK


def gpu(cubes, fname):
    with open(fname, 'w', newline='\n') as f:
        for t, dirs, l16 in cubes:
            f.write(f'CUBE {len(dirs)} {l16:x}\n')
            f.write('T ' + ' '.join(f'{(t >> (64 * j)) & MASK:x}' for j in range(5)) + '\n')
            for d in dirs:
                f.write('D ' + ' '.join(f'{(d >> (64 * j)) & MASK:x}' for j in range(5)) + '\n')
    r = subprocess.run(['wsl', '-d', 'Ubuntu', '--', 'bash', WSLDIR + '/run_gpu.sh', WSLDIR + '/' + fname],
                       capture_output=True, text=True)
    if r.returncode:
        raise SystemExit('GPU run failed: ' + r.stderr[-2000:])
    out = [[int(h, 16) for h in line.split()[2:6]] for line in r.stdout.splitlines() if line.startswith('SUM')]
    assert len(out) == len(cubes), r.stdout[-500:]
    return out


def cpu_sum(t, dirs, l16, chunk=16):
    """numpy cube sum; cubes above 2^chunk points are summed as XOR of sub-cubes (exercises the GPU Gray path)"""
    lo, hi = dirs[:chunk], dirs[chunk:]
    acc = [0, 0, 0, 0]
    for m in range(1 << len(hi)):
        tt = t
        for j, d in enumerate(hi):
            if m >> j & 1:
                tt ^= d
        A = None
        for r, A in S.states(S.cd.points(tt, lo), l16, 6):
            pass
        acc = [a ^ int(np.bitwise_xor.reduce(x)) for a, x in zip(acc, A[:4])]
    return acc


def pick(basis, k, mode):
    if mode == 'basis':
        return rng.sample(basis, k)
    while True:
        d = [S.combine(rng.getrandbits(len(basis)) or 1, basis) for _ in range(k)]
        if S.rank(d) == k:
            return d


if verify:
    p, l16, basis, sym = space(spaces[0])
    cubes = []
    for k in (6, 10, 14, 16, 21, 22):          # k > 20 uses the kernel's per-thread Gray loop
        for _ in range(2):
            cubes.append((S.combine(rng.getrandbits(len(sym)), sym), pick(basis, k, 'span'), l16))
    cubes.append((rng.getrandbits(320), [rng.getrandbits(320) for _ in range(12)], S.NATIVE))
    t0 = time.time()
    g = gpu(cubes, 'gpu_verify_in.txt')
    ok = sum(g[i] == cpu_sum(*c) for i, c in enumerate(cubes))
    print(json.dumps({'gpu_vs_cpu_cube_sums_equal': f'{ok}/{len(cubes)}', 'sec': round(time.time() - t0, 1)}), flush=True)
    if ok != len(cubes):
        raise SystemExit('kernel mismatch')

for tag in spaces:
    p, l16, basis, sym = space(tag)
    for k in dims:
        if k > S.rank(basis):
            continue
        for mode in ('basis', 'span'):
            cubes = [(S.combine(rng.getrandbits(len(sym)), sym), pick(basis, k, mode), l16) for _ in range(ncub)]
            t0 = time.time()
            g = gpu(cubes, f'gpu_in_{tag}_{k}_{mode}.txt')
            nzS = sum(any(s) for s in g)
            nzD = sum(any(x ^ rotp(x, p) for x in s) for s in g)
            wD = sum(sum((x ^ rotp(x, p)).bit_count() for x in s) for s in g) / len(g)
            print(json.dumps({'space': tag, 'round': 6, 'dim': k, 'mode': mode, 'cubes': ncub,
                              'nonzero_digest_sums': nzS, 'nonzero_delta_sums': nzD,
                              'mean_delta_sum_bits': round(wD, 1), 'sec': round(time.time() - t0, 1)}), flush=True)
