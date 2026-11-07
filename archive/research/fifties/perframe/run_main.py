#!/usr/bin/env python3
"""run_main.py - driver of the perframe run (GPU runs in segments). Standard library only.

  python3 -B run_main.py timing              128 frames per arm and generator at K = 512 and 256 (kind 'timing');
                                             writes timing.json with K chosen by SIZING_RULE.txt
  python3 -B run_main.py dry <K> <SEG> <NSEG> code test of driver + analyse_pf.py (kind 'dry run'); dry/
  python3 -B run_main.py main [attempt2]     the preregistered run: checks PREREG.txt against PREREG.sha256, reads
                                             K_TRIALS, SEG_FRAMES, MAX_SEGMENTS, CAP_SECONDS from it; main/
Segment s runs (ctx, G1), (ctrl, G1), (ctx, G2), (ctrl, G2) on frames s*SEG .. (s+1)*SEG - 1 (G = 2^19 outer steps
each). Stop rule (data-independent): segment s >= 1 starts only if elapsed + duration(segment s-1) <= CAP_SECONDS.
Every run dumps its E1L and E3P hits (hitmask 6).
"""
import hashlib
import json
import os
import re
import subprocess
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import seeds  # noqa: E402

ORDER = ((0, 1), (1, 1), (0, 2), (1, 2))


def run1(arm, gen, key, b0, nb, k, out, hits, hitmask=6, launch=64):
    t = time.time()
    p = subprocess.run(["./perframe", "run", str(arm), str(gen), key, str(b0), str(nb), str(k), out, hits,
                        str(hitmask), str(launch)], cwd=HERE, capture_output=True, text=True)
    if p.returncode != 0:
        raise RuntimeError("perframe failed: %s %s" % (p.returncode, p.stderr[-2000:]))
    d = json.loads(p.stdout.strip().splitlines()[-1])
    d["wall"] = time.time() - t
    return d


def segments(kind, K, SEG, NSEG, CAP, outdir, prereg_sha=None):
    os.makedirs(os.path.join(HERE, outdir), exist_ok=True)
    key = {1: seeds.keyhex(kind, 1), 2: seeds.keyhex(kind, 2)}
    log = open(os.path.join(HERE, outdir, "run_log.jsonl"), "a")
    t0, last, done, stop = time.time(), None, 0, "max segments"
    for s in range(NSEG):
        el = time.time() - t0
        if last is not None and el + last > CAP:
            stop = "cap: elapsed %.1f + last segment %.1f > %d" % (el, last, CAP)
            break
        ts = time.time()
        for arm, gen in ORDER:
            tag = "s%02d_a%d_g%d" % (s, arm, gen)
            d = run1(arm, gen, key[gen], s * SEG, SEG, K, os.path.join(outdir, tag + ".bin"),
                     os.path.join(outdir, tag + ".hits"))
            d["tag"], d["segment"] = tag, s
            log.write(json.dumps(d) + "\n"); log.flush()
            print(json.dumps({q: d[q] for q in ("tag", "seconds", "n", "nP", "beta_bad", "e3p_nomask", "t0", "hits")}),
                  flush=True)
        last = time.time() - ts
        done += 1
    out = dict(kind=kind, K=K, SEG=SEG, NSEG=NSEG, CAP=CAP, segments_done=done, frames_per_arm=2 * done * SEG,
               elapsed=time.time() - t0, stop=stop, prereg_sha256=prereg_sha,
               files={f: hashlib.sha256(open(os.path.join(HERE, outdir, f), "rb").read()).hexdigest()
                      for f in sorted(os.listdir(os.path.join(HERE, outdir))) if f.endswith((".bin", ".hits"))})
    json.dump(out, open(os.path.join(HERE, outdir, "run_out.json"), "w"), indent=1)
    print(json.dumps({q: out[q] for q in out if q != "files"}))


def main():
    mode = sys.argv[1]
    if mode == "timing":
        res, t = {}, {}
        for K in (512, 256):
            tot = 0.0
            for arm, gen in ORDER:
                d = run1(arm, gen, seeds.keyhex("timing", gen), 0, 512, K, "timing_tmp.bin", "timing_tmp.hits")
                tot += d["wall"]
                res["k%d_a%d_g%d" % (K, arm, gen)] = d["wall"]
            t[K] = tot / 2048
        os.remove(os.path.join(HERE, "timing_tmp.bin"))
        os.remove(os.path.join(HERE, "timing_tmp.hits"))
        rule = open(os.path.join(HERE, "SIZING_RULE.txt")).read()
        cap = int(re.search(r"CAP_SECONDS = (\d+)", rule).group(1))
        frac = float(re.search(r"MIN_FRACTION = ([0-9.]+)", rule).group(1))
        chosen = next((K for K in (512, 256) if (1 << 19) * t[K] <= frac * cap), 256)
        out = dict(per_frame_seconds={str(K): t[K] for K in t}, runs=res, cap=cap, min_fraction=frac,
                   projected_2p19_frames={str(K): (1 << 19) * t[K] for K in t}, K_chosen=chosen)
        json.dump(out, open(os.path.join(HERE, "timing.json"), "w"), indent=1)
        print(json.dumps(out))
    elif mode == "dry":
        K, SEG, NSEG = int(sys.argv[2]), int(sys.argv[3]), int(sys.argv[4])
        segments("dry run", K, SEG, NSEG, 600, "dry")
    elif mode == "main":
        txt = open(os.path.join(HERE, "PREREG.txt"), "rb").read()
        want = open(os.path.join(HERE, "PREREG.sha256")).read().split()[0]
        got = hashlib.sha256(txt).hexdigest()
        if got != want:
            raise SystemExit("PREREG.txt does not match PREREG.sha256")
        t = txt.decode()
        K = int(re.search(r"^K_TRIALS = (\d+)", t, re.M).group(1))
        SEG = int(re.search(r"^SEG_FRAMES = (\d+)", t, re.M).group(1))
        NSEG = int(re.search(r"^MAX_SEGMENTS = (\d+)", t, re.M).group(1))
        CAP = int(re.search(r"^CAP_SECONDS = (\d+)", t, re.M).group(1))
        attempt2 = len(sys.argv) > 2 and sys.argv[2] == "attempt2"
        segments("main attempt 2" if attempt2 else "main", K, SEG, NSEG, CAP, "main2" if attempt2 else "main",
                 prereg_sha=got)
    else:
        raise SystemExit("unknown mode")


if __name__ == "__main__":
    main()
