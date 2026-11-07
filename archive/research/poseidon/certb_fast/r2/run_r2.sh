#!/bin/bash
# usage: run_r2.sh <centre decimal> <out prefix> [extra engine args]
cd "$(dirname "$0")"
c="$1"; out="$2"; shift 2
nice -n 10 ./certb_fast ddf --F data/F_r2_j0.bin --center "$c" --out "$out" "$@"
