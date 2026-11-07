#!/bin/bash

# Publication root: stable even when this driver changes working directories.
if [ -z "${HASHCYBERAXE_WORKSPACE:-}" ]; then
  _hca_here=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
  while [ ! -d "$_hca_here/research" ] && [ "$_hca_here" != / ]; do _hca_here=$(dirname -- "$_hca_here"); done
  HASHCYBERAXE_WORKSPACE=$_hca_here
fi
export HASHCYBERAXE_WORKSPACE
# Determinism check: rerun the ctx scan into /tmp and diff against the published output.
cd "${HASHCYBERAXE_WORKSPACE}/research/fifties/perspectives/rotational" || exit 1
export OMP_NUM_THREADS=16
/tmp/rotscan_rot ../data ctx /tmp/rot_det_ctx 2>&1 | tail -2
sha256sum /tmp/rot_det_ctx_scan.tsv out_ctx_scan.tsv | cut -c1-16
diff <(cut -f1-9,12- /tmp/rot_det_ctx_scan.tsv) <(cut -f1-9,12- out_ctx_scan.tsv) | head -6
echo "differing lines: $(diff /tmp/rot_det_ctx_scan.tsv out_ctx_scan.tsv | grep -c '^<')"
diff /tmp/rot_det_ctx_scan.tsv out_ctx_scan.tsv | head -4 | cut -c1-200
rm -f /tmp/rot_det_ctx_scan.tsv /tmp/rot_det_ctx_joint.tsv
