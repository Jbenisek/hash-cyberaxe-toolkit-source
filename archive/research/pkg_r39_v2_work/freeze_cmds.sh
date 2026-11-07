
# Publication root: stable even when this driver changes working directories.
if [ -z "${HASHCYBERAXE_WORKSPACE:-}" ]; then
  _hca_here=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
  while [ ! -d "$_hca_here/research" ] && [ "$_hca_here" != / ]; do _hca_here=$(dirname -- "$_hca_here"); done
  HASHCYBERAXE_WORKSPACE=$_hca_here
fi
export HASHCYBERAXE_WORKSPACE
nice -n 10 python3 -B "${HASHCYBERAXE_WORKSPACE}"/research/pkg_r39_v2_work/freeze.py "${HASHCYBERAXE_WORKSPACE}"/research/pkg_r39_s108/sha256/experiments "${HASHCYBERAXE_WORKSPACE}"/research/pkg_r39_best_work/exp > "${HASHCYBERAXE_WORKSPACE}"/research/pkg_r39_v2_work/freeze_s108.json 2> "${HASHCYBERAXE_WORKSPACE}"/research/pkg_r39_v2_work/freeze_s108.err &
nice -n 10 python3 -B "${HASHCYBERAXE_WORKSPACE}"/research/pkg_r39_v2_work/freeze.py "${HASHCYBERAXE_WORKSPACE}"/research/pkg_r39_7111/sha256/experiments "${HASHCYBERAXE_WORKSPACE}"/research/pkg_r39_best_work/exp > "${HASHCYBERAXE_WORKSPACE}"/research/pkg_r39_v2_work/freeze_7111.json 2> "${HASHCYBERAXE_WORKSPACE}"/research/pkg_r39_v2_work/freeze_7111.err &
nice -n 10 python3 -B "${HASHCYBERAXE_WORKSPACE}"/research/pkg_r39_v2_work/freeze.py "${HASHCYBERAXE_WORKSPACE}"/research/pkg_r39_best/sha256/experiments "${HASHCYBERAXE_WORKSPACE}"/research/pkg_r39_best_work/exp > "${HASHCYBERAXE_WORKSPACE}"/research/pkg_r39_v2_work/freeze_best.json 2> "${HASHCYBERAXE_WORKSPACE}"/research/pkg_r39_v2_work/freeze_best.err &
wait
