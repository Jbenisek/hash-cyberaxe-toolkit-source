"""D189 campaign driver: real r=1 odd parts + D185 GPU powering.

The polynomial F is built once with FLINT.  Each centre's monic odd part g is
written as canonical 32-byte Pallas coefficients, D185 computes
q = X^((p-1)/2) mod g on the RTX 3090, and the driver performs the exact gcd
and witness verification locally.  No package or submission is touched.
"""
from __future__ import annotations
import json, math, os, random, shlex, subprocess, sys, time
from pathlib import Path
import flint

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE / "orchard" / "impl"))
from poseidon_ref import hash_reduced  # type: ignore
from d189_real_r1 import P, R, X, INV5, line_setup, build_F, inputs_for_tau, square_root_mod

GPU = HERE / "gpu_ntt" / "d189_gpu"
WORK = HERE / "d189_gpu_work"


def wsl_path(p: Path) -> str:
    s = str(p.resolve()).replace("\\", "/")
    return "/mnt/" + s[0].lower() + "/" + s[3:]


def write_canonical(poly, path: Path):
    with path.open("wb") as f:
        for x in poly.coeffs():
            f.write(int(x).to_bytes(32, "little"))


def read_canonical(path: Path):
    b = path.read_bytes()
    if len(b) % 32: raise ValueError("bad GPU polynomial length")
    return R([int.from_bytes(b[i:i+32], "little") for i in range(0, len(b), 32)])


def gpu_power(gpath: Path, qpath: Path, logpath: Path):
    cmd = "cd {d} && nice -n 10 ./d189_gpu --real-g {g} {q}"
    d = shlex.quote(wsl_path(GPU.parent))
    g = shlex.quote(wsl_path(gpath)); q = shlex.quote(wsl_path(qpath))
    with logpath.open("w", encoding="utf-8") as log:
        cp = subprocess.run(["wsl.exe", "-d", "Ubuntu-22.04", "bash", "-lc", cmd.format(d=d,g=g,q=q)],
                            stdout=log, stderr=subprocess.STDOUT, text=True)
    if cp.returncode: raise RuntimeError(f"D185 GPU failed centre: {cp.returncode}")


def metrics(g, q, c, line):
    # q = X^e mod g, e=(p-1)/2.  Thus q-1 detects nonzero squares and
    # X*(q^2-1) is X^p-X modulo g, detecting all field roots.
    H = g.gcd((q - 1) % g)
    rootpoly = (X * ((q * q - 1) % g)) % g
    roots = g.gcd(rootpoly)
    rep = g.gcd(g.derivative())
    verified = []
    for root, _mult in H.roots()[:4]:
        s = square_root_mod(int(root))
        if s is None or s == 0: continue
        wp, wm = (c + s) % P, (c - s) % P
        nk, rho = inputs_for_tau(pow(wp, INV5, P), line)
        nk2, rho2 = inputs_for_tau(pow(wm, INV5, P), line)
        h0, h1 = hash_reduced(nk, rho, 1), hash_reduced(nk2, rho2, 1)
        if h0 != h1: raise AssertionError("reference collision verification failed")
        verified.append({"S": int(root), "hash": int(h0), "inputs_distinct": (nk, rho) != (nk2, rho2)})
    return {"roots": int(roots.degree()), "nonzero_square_roots": int(H.degree()),
            "squarefree": rep.degree() == 0, "repeated_factor_degree": int(rep.degree()),
            "verified": verified}


def main():
    n = int(sys.argv[1]) if len(sys.argv) > 1 else 12
    seed = int(sys.argv[2]) if len(sys.argv) > 2 else 18920261012
    out = Path(sys.argv[3]) if len(sys.argv) > 3 else HERE / "d189_gpu_results.jsonl"
    line_idx = int(sys.argv[4]) if len(sys.argv) > 4 else 0
    WORK.mkdir(exist_ok=True)
    print("building real r=1 F degree 78125", flush=True)
    line = line_setup(line_idx); F = build_F(line)
    for tau in (0,1,2,7,12345):
        nk, rho = inputs_for_tau(tau, line)
        assert int(F.evaluate(pow(tau, 5, P))) == hash_reduced(nk, rho, 1)
    print("validated_degree", F.degree(), "direct_checks", 5, flush=True)
    rng = random.Random(seed); rows = []; t0 = time.time()
    with out.open("w", encoding="utf-8") as fp:
        for i in range(n):
            c = rng.randrange(P)
            # Build g(s^2) by the exact factorial Taylor shift.
            from d189_real_r1 import shifted_coeffs
            sh = shifted_coeffs(F, c)
            g = R([sh[2*k+1] for k in range((F.degree()+1)//2)]).monic()
            gp = WORK / f"g_{i:03d}.bin"; qp = WORK / f"q_{i:03d}.bin"; lp = WORK / f"gpu_{i:03d}.txt"
            write_canonical(g, gp)
            t1 = time.time(); gpu_power(gp, qp, lp); gpu_s = time.time() - t1
            q = read_canonical(qp)
            t2 = time.time(); m = metrics(g, q, c, line); gcd_s = time.time() - t2
            row = {"index": i, "line": line_idx, "seed": seed, "center": str(c), "gpu_seconds": round(gpu_s,3), "gcd_seconds": round(gcd_s,3), **m}
            fp.write(json.dumps(row, sort_keys=True) + "\n"); fp.flush(); rows.append(row)
            print("centre", i, "roots", row["roots"], "nonzero_square", row["nonzero_square_roots"],
                  "squarefree", row["squarefree"], "gpu_s", row["gpu_seconds"],
                  "verified", len(row["verified"]), flush=True)
    succ = sum(r["nonzero_square_roots"] > 0 for r in rows)
    print("SUMMARY", json.dumps({"n": n, "success": succ, "fraction": succ/n if n else None,
                                  "expected": 1-math.exp(-.5), "elapsed_s": round(time.time()-t0,3), "out": str(out)}), flush=True)


if __name__ == "__main__": main()
