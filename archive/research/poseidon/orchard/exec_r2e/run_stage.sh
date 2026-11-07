#!/bin/bash
# stage the final package only (nothing is submitted): file_pkg.sh with --stage-only, base = the accepted r2d package
W='historical-sources/~~Projects/~HashSmash/workspace'
cd "$W"
bash research/launch/file_pkg.sh pareto poseidon 2 research/poseidon/orchard/exec_r2e/pkg_final --base research/poseidon/orchard/exec_r2d/pkg_check_exec --stage-only 2>&1 | tail -40
