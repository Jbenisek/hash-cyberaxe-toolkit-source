#!/usr/bin/env python3
"""Copies of the result files of the groundwork that the text of pkg6 quotes. Research helper, not submitted.

    python -B tools/fetch_h8.py

Copies each file below from research/h8 (or research/night/main) into evidence/h8/ and writes
evidence/h8/SOURCES.txt: one line per file with its source, size, time of the source file and SHA-256. The data
module reads the copies and nothing else of the groundwork, so the text does not move with a job that is still
writing. Run it again to take the files as they are now; the build then shows what changed.
"""
import hashlib
import shutil
import sys
import time
from pathlib import Path

sys.dont_write_bytecode = True
PKG = Path(__file__).resolve().parent.parent
RESEARCH = PKG.parent
OUT = PKG / "evidence" / "h8"
FILES = (
    "h8/counts/H8_count.txt", "h8/counts/check_e1_amc.txt", "h8/counts/check_e3_amc.txt", "h8/counts/check_bf8.txt",
    "h8/counts/betas_histogram.txt", "h8/counts/sysall_by_k.txt", "h8/counts/members_H8.txt",
    "h8/design/DESIGN.txt", "h8/design/h8_ref_check.txt",
    "h8/batch/H8_conservative.txt", "h8/batch/H8_sat_summary.txt", "h8/batch/H8_passrate.txt", "h8/batch/H8_fullcheck.txt",
    "h8/batch/H8_cost.txt", "h8/batch/big_two.json",
    "h8/gpu/out/H8_gpu_compare.txt", "h8/gpu/out/h8_deep_expected.txt", "h8/gpu/out/h8_check.txt", "h8/gpu/out/h8_regress.txt",
    "h8/gpu/out/h8_ctx_independent.txt", "h8/gpu/out/h8_ctx_run1_consecutive.txt", "h8/gpu/out/h8_ctx_run1_spread.txt",
    "h8/gpu/out/h8_layout.txt", "h8/gpu/out/h8_runs.log", "h8/gpu/out/e3partial_bf8_H8.txt",
    "h8/gpu_more/out/h8_layout_more.txt",
    "h8/reports/r1_gpu.txt", "h8/reports/r4_gpt_sol_recount.txt",
    "night/main/trail5_lx.log", "night/main/cand_exact_lx.txt",
    "h8/gpu/out/e3p_expected_H8.txt", "h8/gpu_more/out/h8_deep_more.txt",
)
# The raw result files of the runs on the graphics card, one file per run; they go to evidence/h8/runs/. The data
# module pools them itself (pkg6_data.read_runs), so that runs finished after the groundwork's comparing file
# (H8_gpu_compare.txt) was written are in the text. A run that is still being written (a file below 3,000 bytes) is
# left out; the runs with seeds 8201.. are taken as far as they are finished.
RUNS = (["h8/gpu/out/h8_real40.txt", "h8/gpu/out/h8_real42.txt", "h8/gpu/out/h8_real45.txt",
         "h8/gpu/out/h8_model40.txt", "h8/gpu/out/h8_model42.txt", "h8/gpu/out/h8_model44.txt"]
        + [f"h8/gpu/out/h8_layout_run{i}.txt" for i in range(1, 9)]
        + [f"h8/gpu_more/out/h8_layout_run{i}.txt" for i in range(9, 25)]
        + [f"h8/gpu/out/h8_spread_run{i}.txt" for i in range(1, 9)])
RUNS_GLOB = ("h8/gpu_more/out", "h8_real45_seed*.txt")
COMPLETE = 3000


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "runs").mkdir(exist_ok=True)
    lines, missing, unfinished = ["file | source | bytes | source last written | sha256"], [], []
    seeds = sorted(p for p in (RESEARCH / RUNS_GLOB[0]).glob(RUNS_GLOB[1]))
    jobs = [(rel, OUT) for rel in FILES] + [(rel, OUT / "runs") for rel in RUNS] \
        + [(f"{RUNS_GLOB[0]}/{p.name}", OUT / "runs") for p in seeds]
    for old in (OUT / "runs").glob("*.txt"):
        old.unlink()
    for rel, folder in jobs:
        src = RESEARCH / rel
        if not src.exists():
            missing.append(rel)
            continue
        if folder != OUT and src.stat().st_size < COMPLETE:
            unfinished.append(src.name)
            continue
        dst = folder / src.name
        shutil.copyfile(src, dst)
        raw = dst.read_bytes()
        stamp = time.strftime("%Y-%m-%d %H:%M", time.localtime(src.stat().st_mtime))
        name = src.name if folder == OUT else "runs/" + src.name
        lines.append(f"{name} | research/{rel} | {len(raw)} | {stamp} | {hashlib.sha256(raw).hexdigest()}")
    (OUT / "SOURCES.txt").write_text("\n".join(lines) + "\n", encoding="ascii", newline="\n")
    print(f"copied {len(lines) - 1} files to evidence/h8 ({sum(1 for l in lines if l.startswith('runs/'))} of them run files); "
          f"missing: {missing if missing else 'none'}; runs not finished and left out: {unfinished if unfinished else 'none'}")
    return 1 if missing else 0


if __name__ == "__main__":
    sys.exit(main())
