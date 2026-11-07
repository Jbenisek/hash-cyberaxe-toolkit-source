#!/bin/bash

# Publication root: stable even when this driver changes working directories.
if [ -z "${HASHCYBERAXE_WORKSPACE:-}" ]; then
  _hca_here=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
  while [ ! -d "$_hca_here/research" ] && [ "$_hca_here" != / ]; do _hca_here=$(dirname -- "$_hca_here"); done
  HASHCYBERAXE_WORKSPACE=$_hca_here
fi
export HASHCYBERAXE_WORKSPACE
# Validation of perframe.cu against ref_pf.py (kind 'validate'); writes val/VALIDATION.json
set -e
cd "${HASHCYBERAXE_WORKSPACE}/research/fifties/perframe"
mkdir -p val
read K1 K2 < <(python3 -B seeds.py validate)
FILES=()
for a in 0 1; do for g in 1 2; do
  ./perframe val $a $g $([ $g = 1 ] && echo $K1 || echo $K2) 0 32 64 16 val/v_small_a${a}_g${g}.bin > /dev/null
  ./perframe val $a $g $([ $g = 1 ] && echo $K1 || echo $K2) 100 4 64 64 val/v_k64_a${a}_g${g}.bin > /dev/null
  ./perframe val $a $g $([ $g = 1 ] && echo $K1 || echo $K2) 200 2 16 1024 val/v_k1024_a${a}_g${g}.bin > /dev/null
  ./perframe val $a $g $([ $g = 1 ] && echo $K1 || echo $K2) 300 2 8192 16 val/v_big_a${a}_g${g}.bin > /dev/null
  ./perframe run $a $g $([ $g = 1 ] && echo $K1 || echo $K2) 300 2 16 val/r_big_a${a}_g${g}.bin val/r_big_a${a}_g${g}.hits 0 64 8192 > /dev/null
  FILES+=(val/v_small_a${a}_g${g}.bin val/v_k64_a${a}_g${g}.bin val/v_k1024_a${a}_g${g}.bin val/v_big_a${a}_g${g}.bin)
done; done
python3 -B ref_pf.py val $K1 $K2 "${FILES[@]}" > val/val_check.json
python3 -B ref_pf.py cmp val/v_big_a0_g1.bin val/r_big_a0_g1.bin val/v_big_a1_g1.bin val/r_big_a1_g1.bin \
  val/v_big_a0_g2.bin val/r_big_a0_g2.bin val/v_big_a1_g2.bin val/r_big_a1_g2.bin > val/cmp_check.json
# full size: G = 2^19, k = 512, 16 frames per arm and generator; every E1L, E3P and R24 hit recomputed
HF=()
for a in 0 1; do for g in 1 2; do
  ./perframe run $a $g $([ $g = 1 ] && echo $K1 || echo $K2) 1000 16 512 val/full_a${a}_g${g}.bin val/full_a${a}_g${g}.hits 22 16 > val/full_a${a}_g${g}.json
  HF+=(val/full_a${a}_g${g}.hits)
done; done
python3 -B ref_pf.py hits $K1 $K2 "${HF[@]}" > val/hits_check.json
sha256sum perframe perframe.cu pf_consts.cuh gen_consts.py ref_pf.py > val/code.sha256
python3 -B - <<'EOF'
import json
v = json.load(open("val/val_check.json")); c = json.load(open("val/cmp_check.json")); h = json.load(open("val/hits_check.json"))
full = [json.load(open("val/full_a%d_g%d.json" % (a, g))) for a in (0, 1) for g in (1, 2)]
ok = v["mismatches"] == 0 and not v["fails"] and c["all_equal"] and h["hits"] == h["ok"] and h["hits"] > 0
out = {"PASS": ok, "val_mismatches": v["mismatches"], "val_fails": v["fails"], "frames": v["frames"], "steps": v["steps"],
       "trials": v["trials"], "valid": v["valid"], "lane_ok": v["lane_ok"], "r_identity": v["r_identity"],
       "events": v["events"], "pairs_within": v["pairs_within"], "pairs_same_c1": v["pairs_same_c1"],
       "cmp_all_equal": c["all_equal"], "hits": h["hits"], "hits_ok": h["ok"], "hits_by_bit": h["by_event_bit"],
       "full_runs": [{q: f[q] for q in ("arm", "gen", "seconds", "n", "nP", "beta_bad", "e3p_nomask", "t0", "pc_mismatch", "hits")} for f in full]}
json.dump(out, open("val/VALIDATION.json", "w"), indent=1)
print(json.dumps(out))
EOF
