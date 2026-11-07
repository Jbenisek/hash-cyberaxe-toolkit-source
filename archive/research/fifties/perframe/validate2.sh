#!/bin/bash

# Publication root: stable even when this driver changes working directories.
if [ -z "${HASHCYBERAXE_WORKSPACE:-}" ]; then
  _hca_here=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
  while [ ! -d "$_hca_here/research" ] && [ "$_hca_here" != / ]; do _hca_here=$(dirname -- "$_hca_here"); done
  HASHCYBERAXE_WORKSPACE=$_hca_here
fi
export HASHCYBERAXE_WORKSPACE
# Validation part 2 (kind 'validate'): full size G = 2^19, k = 512, 256 frames per arm and generator (blocks 2000..),
# every E1L and E3P hit recomputed by ref_pf.py (real compressions); writes val/VALIDATION2.json
set -e
cd "${HASHCYBERAXE_WORKSPACE}/research/fifties/perframe"
read K1 K2 < <(python3 -B seeds.py validate)
HF=()
for a in 0 1; do for g in 1 2; do
  ./perframe run $a $g $([ $g = 1 ] && echo $K1 || echo $K2) 2000 256 512 val/deep_a${a}_g${g}.bin val/deep_a${a}_g${g}.hits 6 64 > val/deep_a${a}_g${g}.json
  HF+=(val/deep_a${a}_g${g}.hits)
done; done
python3 -B ref_pf.py hits $K1 $K2 "${HF[@]}" > val/hits2_check.json
python3 -B - <<'EOF'
import json
h = json.load(open("val/hits2_check.json"))
runs = [json.load(open("val/deep_a%d_g%d.json" % (a, g))) for a in (0, 1) for g in (1, 2)]
out = {"PASS": h["hits"] == h["ok"] and h["hits"] > 0, "hits": h["hits"], "ok": h["ok"], "by_bit": h["by_event_bit"],
       "cv_zero_words_E1L": h["cv_zero_words_hist_E1L"], "cv_zero_words_E3P": h["cv_zero_words_hist_E3P"],
       "runs": [{q: r[q] for q in ("arm", "gen", "seconds", "trials", "n", "nP", "e3p_nomask", "t0", "pc_mismatch", "e1l_ra", "e3p_ra")} for r in runs]}
json.dump(out, open("val/VALIDATION2.json", "w"), indent=1)
print(json.dumps(out))
EOF
