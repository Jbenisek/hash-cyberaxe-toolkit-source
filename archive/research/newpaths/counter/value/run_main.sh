#!/bin/bash

# Publication root: stable even when this driver changes working directories.
if [ -z "${HASHCYBERAXE_WORKSPACE:-}" ]; then
  _hca_here=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
  while [ ! -d "$_hca_here/research" ] && [ "$_hca_here" != / ]; do _hca_here=$(dirname -- "$_hca_here"); done
  HASHCYBERAXE_WORKSPACE=$_hca_here
fi
export HASHCYBERAXE_WORKSPACE
# four background rate runs, 2^36 trials each, time limit 1 h each; PIDs in my_pids.txt (counter/value)
D="${HASHCYBERAXE_WORKSPACE}"/research/newpaths/counter/value
cd "$D" || exit 1
mkdir -p out
: > my_pids.txt
nohup timeout 3600 ./ctr_rates rates 20 16 1 1 11 > out/r_sub_cube_s11.txt 2> out/r_sub_cube_s11.err &
echo "$! r_sub_cube_s11" >> my_pids.txt
nohup timeout 3600 ./ctr_rates rates 20 16 1 1 12 > out/r_sub_cube_s12.txt 2> out/r_sub_cube_s12.err &
echo "$! r_sub_cube_s12" >> my_pids.txt
nohup timeout 3600 ./ctr_rates rates 20 16 0 1 13 > out/r_all_cube_s13.txt 2> out/r_all_cube_s13.err &
echo "$! r_all_cube_s13" >> my_pids.txt
nohup timeout 3600 ./ctr_rates rates 20 16 0 0 14 > out/r_all_free_s14.txt 2> out/r_all_free_s14.err &
echo "$! r_all_free_s14" >> my_pids.txt
cat my_pids.txt
