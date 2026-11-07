#!/usr/bin/env bash
# Step 3: pin H8, class 830303cf, a cube of it, rules on h1, with pair_calc_sub (the 60 betas that carry mass in the
# full class, h8_betas_pos.txt = the list of research/h8/rule_exact; a cube is a subset of the class, so no other
# beta can carry mass in it).
#   c03_run.sh NAME CUBE_MASK CUBE_VALUE RULESET [PROCESSES=4] [extra arguments of pair_calc_sub]
#   CUBE_MASK none = the full class.   RULESET cube | full   (see below)
# One single-threaded process per slice of the list, nice -n 5. Result: NAME.out in this folder.
set -uo pipefail
W='historical-sources/~~Projects/~HashSmash/workspace'
H="$W/research/pkg7/count"
S="$HOME/hashsmash/pkg7_count"; B="$S/bin"; O="$S/out"
ARGS="fdb77cfd 0a08818b fffffff8 8127c181 830303cf"; Y11=7af77f38
NAME=$1; CM=$2; CV=$3; RS=$4; P=${5:-4}; shift 5 || shift $#
# h1 conditions "XOR of the bits in MASK = V". F = the five-row core of gpt_sol_answer_M.md.
F="00030000:0,00000404:1,00000808:1,00000001:0,00000002:1"       # h16^h17=0, h2^h10=1, h3^h11=1, h0=0, h1=1
OLD6="00010000:0,00020000:0,00000001:0,00000002:1,00000404:1,00000808:1"   # h16=0, h17=0, h0=0, h1=1, h2^h10=1, h3^h11=1
PP="01001008:0"; QQ="02002040:0"                                 # P: h3^h12^h24 = 0;  Q: h6^h13^h25 = 0
R4="00000001:0,00000002:1,00010000:0,00020000:0"; R5="$R4,0000000c:1"      # the rules 4 and 5 of pkg6 (5 = the filed one)
if [ "$RS" = cube ]; then    # F5, old6, S6, S7, S8, S9, p5, p4
  RULES="-rule $F -rule $OLD6 -rule $F,$PP -rule $F,$PP,$QQ -rule $OLD6,$PP,$QQ -rule $OLD6,$PP,$QQ,0000000c:1 -rule $R5 -rule $R4"
else                         # F5, old6, K7, K8 (gpt_sol_answer_K.md), S6, S7, S8, p5
  RULES="-rule $F -rule $OLD6 -rule $OLD6,00000c00:1 -rule $OLD6,0000000c:1,61000000:1 -rule $F,$PP -rule $F,$PP,$QQ -rule $OLD6,$PP,$QQ -rule $R5"
fi
CUBE=""; [ "$CM" != none ] && CUBE="-cube $CM $CV"
L="$H/h8_betas_pos.txt"; D="$O/$NAME.d"; mkdir -p "$D"; rm -f "$D"/*
for i in $(seq 0 $((P - 1))); do awk -v p="$P" -v i="$i" '(NR - 1) % p == i' "$L" > "$D/slice_$i.lst"; done
t0=$(date +%s)
seq 0 $((P - 1)) | xargs -P "$P" -I{} sh -c "OMP_NUM_THREADS=1 nice -n 5 '$B/pair_calc_sub' $ARGS '$D/slice_{}.lst' $Y11 $RULES $CUBE -mode both $* > '$D/raw_{}.out' 2> '$D/raw_{}.err'"
cat "$D"/raw_*.out > "$O/$NAME.out"; cp "$O/$NAME.out" "$H/$NAME.out"
echo "$NAME: cube $CM $CV rules $RS, $(wc -l < "$L") betas in $P slices, seconds $(( $(date +%s) - t0 )), DONE lines $(grep -c '^DONE' "$O/$NAME.out"), stderr lines $(cat "$D"/raw_*.err | wc -l), binary $(sha256sum "$B/pair_calc_sub" | cut -c1-16)" | tee -a "$H/runs.log"
