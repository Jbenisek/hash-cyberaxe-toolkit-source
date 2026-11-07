#!/bin/bash
# traillab known-answer tests (make test). Worked backwards: every expected number comes from an earlier, independent
# program or proof of ours, and the tool must reproduce it. A failing test is fixed in the tool, not in the expected value.
#   [K1] Table-17 pair            ePrint 2026/1120 Table 17; REFERENCE_CARD; expansion_audit/w22/RESULT.md (control)
#   [K2] rows 22..36 uniform       rows22_24/automaton/RESULT.md (r2224.c enum, consts)
#   [K3] real-pipeline ratio       rows22_24/automaton/RESULT.md section 3 (2.4648 +- 0.0145, 2^31 proposals)
#   [K4] four patterns             grok/in/job103_lowmem/r37_unforced.md; pkgR37P proof 7.7 / B.3 (q3 gain 1.98)
#   [K5] expansion artifact        expansion_audit/w22/RESULT.md, expansion_audit/why/RESULT.md
#   [K6] row-16 table              r37 proof (7319bba9) section 6.2: 1,052,672 pairs, 1,042,240 distinct u
#   [K7] study-B q3                r37 proof (7319bba9) section 7.4: mean 2^-73.9987, 32 replicates, rel. sd 0.0378
#   [X]  further cross-checks      allg_classes, smc_exact selftest, R38M fam38.c / r16enum.py, job104 measure.c
# QUICK=1 skips the 2^32 enumerations and uses smaller Monte-Carlo runs (the interval tests then widen with their error bars).
cd "$(dirname "$0")/.." || exit 2
T=./traillab; PASS=0; FAIL=0; T0=$(date +%s)
ok()   { echo "PASS  $1"; PASS=$((PASS+1)); }
bad()  { echo "FAIL  $1"; echo "      got: $2"; FAIL=$((FAIL+1)); }
expect() { # name, command output, grep pattern, pattern for the 'got' line
  if echo "$2" | grep -qE "$3"; then ok "$1"; else bad "$1" "$(echo "$2" | grep -E "$4" | head -3)"; fi; }
fcheck() { # name, awk condition on v, value
  awk -v v="$3" "BEGIN{exit !($2)}" && ok "$1 [$3]" || bad "$1" "$3"; }
lap() { echo "      (elapsed $(( $(date +%s) - T0 )) s)"; }

echo "== [K1] Table-17 pair: SHA-256 reference, both published pairs, every printed condition, model consistency"
for c in chi37 chi38; do
  o=$($T check --chi chi/$c.txt --n 20000)
  expect "$c: SHA-256 selftest" "$o" "reference .* ok" "SHA"
  expect "$c: published outputs equal and digest matches" "$o" "outputs EQUAL; digest matches" "published pair:"
  expect "$c: 0 failing rows (printed and model conditions; rows -4..-1 = CV carry no conditions)" "$o" "\(rows 0\.\.3[67]\): 0 failing rows; vs the attack model's conditions: 0" "failing"
  expect "$c: rebuild of published coordinates exact" "$o" "consistent, 0 differing" "rebuild"
  expect "$c: random draws: consistent, replay/expansion/incremental 0" "$o" "inconsistent 0; x forward replay mismatches 0; y expansion mismatches 0; incremental-vs-full mismatches 0" "random coordinates"
  [ $c = chi37 ] && expect "chi37: equal 37-step digests a856d46e 4b46eb28 4935248c 92a2fc98 e0fb2610 10a9951f 54264f5b 80954580" "$o" "outputs EQUAL; digest matches the file \(a856d46e 4b46eb28 4935248c 92a2fc98 e0fb2610 10a9951f 54264f5b 80954580\)" "published pair:"
  [ $c = chi38 ] && expect "chi38: equal 38-step digests 5d9ca5f4 ..." "$o" "outputs EQUAL; digest matches the file \(5d9ca5f4 59ace3a3" "published pair:"
done
lap

echo "== [K2] rows 22..36, uniform exact model (r2224 enum and consts, PROVED there by 2^32 loops)"
o=$($T sdiff --delta 017f8000 --func s1 --out 4fff9f30 --chi chi/chi37.txt --cell W22 --limit 8)
expect "chi37 W22 exact set 9,830,400 = 75*2^17 vs cell 4,194,304 = 2^22" "$o" "EXACT count 9830400 .* cell 4194304" "SDIFF"
expect "chi37 W22: 6 XOR patterns, chi pattern 32/75" "$o" "xor 01808000  w  3  count      4194304  share 0.426667" "xor 0180"
n22=$(echo "$o" | grep -oE "EXACT count [0-9]+" | awk '{print $3}'); c22=$(echo "$o" | grep -oE "printed cell [0-9]+" | awk '{print $3}')
o=$($T sdiff --delta 20000000 --func s1 --out fff80c00 --chi chi/chi37.txt --cell W24 --limit 4)
expect "chi37 W24 exact set 285,212,672 = 17*2^24 vs cell 2^28" "$o" "EXACT count 285212672 .* cell 268435456" "SDIFF"
n24=$(echo "$o" | grep -oE "EXACT count [0-9]+" | awk '{print $3}'); c24=$(echo "$o" | grep -oE "printed cell [0-9]+" | awk '{print $3}')
# q_event/q_cell in the uniform W22/W24 model = (|S_ex22|/|S_cell22|) (|S_ex24|/|S_cell24|) (E22[29] costs 1/2 in both): integer identity
if [ -n "$n22" ] && [ -n "$c24" ] && [ $(( n22 * n24 * 512 )) -eq $(( c22 * c24 * 1275 )) ]; then ok "uniform q_event/q_cell = ($n22/$c22)($n24/$c24) = 1275/512 exactly"; else bad "uniform q_event/q_cell = 1275/512" "$n22/$c22 x $n24/$c24"; fi
o=$($T sdiff --delta 20000000 --maxhw 32 --limit 4)
expect "signed representations of 2^29 cover all 2^32 words (mass 1)" "$o" "probability mass 1.0000000000" "mass"
o=$($T backward --chi chi/chi37.txt --rows 22 22 --noenum)
expect "chi37 row 22: X_E = 0 with Pr 1 (E21[29]=0 blocks the CH path)" "$o" "needed X = 00000000 : Pr 1 " "needed X"
expect "chi37 row 22: only W22 signing (24n,23n,15u) holds" "$o" "=======nn=======u===============  mod 017f8000  Pr\[row holds\] 1   <- characteristic" "signings|nn=="
n=$(echo "$o" | grep -A9 "alternative signings of W_t" | grep -c "Pr\[row holds\] 0$")
[ "$n" = "7" ] && ok "chi37 row 22: the other 7 W22 signings have Pr 0" || bad "chi37 row 22: the other 7 W22 signings have Pr 0" "$n"
expect "chi37 schedule: dW23 = 0 PROVED" "$o" "W23: dW = 00000000 PROVED" "W23"
expect "chi37 schedule: dW25 = 0 PROVED" "$o" "W25: dW = 00000000 PROVED" "W25"
expect "chi37 schedule: dW26 value-dependent, requires s1(W24+2^29)-s1(W24) = fff80c00" "$o" "W26: .*requires s1\(W24 \+ 20000000\) - s1\(W24\) = fff80c00" "W26"
expect "chi37 schedule: dW24 requires s1(W22+017f8000)-s1(W22) = 4fff9f30" "$o" "W24: .*requires s1\(W22 \+ 017f8000\) - s1\(W22\) = 4fff9f30" "W24"
lap

echo "== [K3]+[K2 eq] real pipeline, chi37 rows 22..36 (r2224 validate: EXACT/cells 2.4648 +- 0.0145; eq36 <=> eq24 and dW26 = 0)"
if [ -n "$QUICK" ]; then A="--np 1024 --mt 8192"; else A="--np 4096 --mt 32768"; fi
o=$($T window --chi chi/chi37.txt --rows 22 36 --event out $A --relax R2disputed --equiv 24,26 --seeds 11,12 --quiet)
echo "$o" | grep -E "^== summary|prefix log2" | sed 's/^/      /'
r=$(echo "$o" | grep -oE "summary over [0-9]+ seed\(s\): EXACT/cells [0-9.]+ \+- [0-9.]+" | awk '{print $6}')
h=$(echo "$o" | grep -oE "summary over [0-9]+ seed\(s\): EXACT/cells [0-9.]+ \+- [0-9.]+" | awk '{print $8}')
fcheck "chi37 EXACT/cells $r +- $h overlaps the known 2.4648 +- 0.0145" "(v - 2.4648)^2 <= (0.0145 + $h)^2" "$r"
p=$(echo "$o" | grep -oE "prefix log2 P\(rows 4\.\.21\) = -[0-9.]+" | head -1 | awk '{print $NF}')
fcheck "chi37 log2 P(rows 4..21) about -59.0 (r2224 SMC states -58.98..-59.01)" "v > -59.3 && v < -58.7" "$p"
expect "chi37 replay/consistency diagnostics 0" "$o" "prefix broken by redraw 0, y-anchor inconsistent 0, replay mismatches 0" "samples"
expect "chi37 eq36 <=> (eq24 and dW26 = 0): 0 counterexamples either way, every sample" "$o" "equivalence counts pooled: predicate and EXACT [1-9][0-9]* ; predicate, not EXACT 0 ; EXACT, not predicate 0" "equivalence counts"
r2=$(echo "$o" | grep -oE "R2disputed/cells [0-9.]+" | head -1 | awk '{print $2}')
[ "$r2" = "1.00000" ] && ok "[K5] chi37 W22 bits 26,17,13 dropped: ratio exactly $r2 with the real expansion (not free)" || bad "[K5] R2disputed ratio 1" "$r2"
lap

echo "== [K4] four patterns of rows 18/19 (r37_unforced.md; pkgR37P)"
LIN='LIN=droprow E18 ; droprow E19 ; droprow A18 ; droprow A19 ; droprow W18 ; droprow W19 ; lin E18[1]^E18[11]=0 ; lin E18[1]^E18[28]=1 ; lin E18[10]^E18[29]=0 ; lin E18[10]^E19[29]=0 ; lin E18[5]^E18[18]=0 ; lin E18[5]^E18[1]^E18[10]=0'
o=$($T exact --chi chi/chi37.txt --rows 18 19 --event state --enum E18:mask:30040c22 --enum E19:mask:20000000 --relax "$LIN" --hist LIN)
expect "the 6 parities admit exactly 4 of the 256 patterns of the 8 value bits" "$o" "values passing the prefix and LIN: 4 distinct" "distinct"
expect "the printed pattern (E18 bits 1,10,11,29 = 1; E19[29] = 1) is one of them" "$o" "E18 bits 20000c02  E19 bits 20000000  : 1" "E18 bits"
NB=512; [ -n "$QUICK" ] && NB=128
o=$($T exact --chi chi/chi37.txt --rows 18 21 --event state --enum E18:mask:30040c22 --enum E19:mask:20000000 --relax R1 --relax 'R1v=dropv E18 30040c22 ; dropv E19 20000000' --hist R1v --base smc --np 2048 --pick $NB --seed 41)
echo "$o" | grep -E "^\[sum\]" | sed 's/^/      /'
c=$(echo "$o" | grep -E "^\[sum\]   cells " | grep -oE "with prefix [0-9]+" | head -1 | awk '{print $3}')
a=$(echo "$o" | grep -E "^\[sum\]   R1 " | grep -oE "with prefix [0-9]+" | head -1 | awk '{print $3}')
b=$(echo "$o" | grep -E "^\[sum\]   R1v " | grep -oE "with prefix [0-9]+" | head -1 | awk '{print $3}')
[ -n "$a" ] && [ "$a" = "$b" ] && ok "the 8 value conditions reduce to the 6 parities: on $NB SMC prefixes, rows 18..21 pass $b times without the 8 values and $a times with the parities (equal)" || bad "8 values = 6 parities" "R1 $a, R1v $b"
expect "exactly 4 patterns occur on the SMC prefixes (none outside the parity set)" "$o" "^\[sum\]   enumerated values passing the prefix and R1v: 4 distinct" "distinct"
g=$(awk -v a="$a" -v c="$c" 'BEGIN{printf "%.3f", log(a/c)/log(2)}')
fcheck "rows 18..21 over $NB prefixes: parities/cells = $a/$c, gain $g bits (structural 2.00; r37_unforced 1.93 [1.78, 2.09])" "v > 1.70 && v < 2.30" "$g"
lap

echo "== [K7]+[K4 q3] q3 = P(rows 4..36, model cells) on random prefixes, cells vs the four patterns (study B 2^-73.9987; pkgR37P gain 1.98)"
if [ -n "$QUICK" ]; then Q="--np 4096 --m 512 --mt 2048 --seeds 31,32"; NS=2; else Q="--np 8192 --m 512 --mt 4096 --seeds 31,32,33,34"; NS=4; fi
o=$($T window --chi chi/chi37.txt --rows 22 36 --event out $Q --quiet)
o2=$($T window --chi chi/chi37.txt --rows 22 36 --event out $Q --quiet --prefix-relax R1)
q=$(echo "$o" | grep -oE "summary: log2 P\(rows 4\.\.36, model cells\) mean -[0-9.]+, seed sd [0-9.]+" | awk '{print $8, $11}' | tr -d ',')
q2=$(echo "$o2" | grep -oE "summary: log2 P\(rows 4\.\.36, model cells\) mean -[0-9.]+, seed sd [0-9.]+" | awk '{print $8, $11}' | tr -d ',')
echo "      cells: mean, seed sd = $q ; four patterns: $q2 ($NS seeds each)"
qm=${q% *}; qs=${q#* }; q2m=${q2% *}; q2s=${q2#* }
# study B: 32 replicates, log2 sd 0.0378/ln2 = 0.0545. Tolerance: 3 standard errors of the difference of the two means.
fcheck "[K7] chi37 q3 (cells) $qm vs study B mean -73.9987 (99% bound -74.0225)" "(v + 73.9987)^2 <= 9 * (0.0545^2/32 + (($qs > 0.0545 ? $qs : 0.0545)^2)/$NS)" "$qm"
gq=$(awk -v a="$q2m" -v b="$qm" 'BEGIN{printf "%.4f", a-b}')
fcheck "[K4] q3 gain of the four patterns $gq bits (known 1.98..2.01)" "(v - 2.0)^2 <= 9 * ((($qs > 0.0545 ? $qs : 0.0545)^2) + (($q2s > 0.0545 ? $q2s : 0.0545)^2))/$NS" "$gq"
lap

echo "== [K5] expansion artifact (expansion_audit w22 and why)"
o=$($T flip --chi chi/chi37.txt --word W22 --mask 04022000)
exp37="000:80000100 100:a0000100 010:00000000 110:20000000 001:80000000 101:a0000000 011:00000100 111:20000100"
okn=0; for e in $exp37; do echo "$o" | grep -qE "pattern ${e%%:*}: ds1\(W22\) [0-9a-f]+  dW24 ${e##*:} " && okn=$((okn+1)); done
[ $okn = 8 ] && ok "chi37 W22 bits (13,17,26): all 8 re-expanded dW24 values equal the w22 audit table" || bad "chi37 W22 dW24 table" "$okn of 8 match"
expect "chi37 W22: only the printed pattern 110 keeps dW24 = 20000000 (bits NOT free)" "$o" "FLIP result: 1 of 8 patterns keep every later modular difference \(only the published pattern\)" "FLIP result"
o=$($T flip --chi chi/chi38.txt --word W23 --mask 04022000)
exp38="000:80000000 100:a0000000 010:00000100 110:20000100 001:80000100 101:a0000100 011:00000000 111:20000000"
okn=0; for e in $exp38; do echo "$o" | grep -qE "pattern ${e%%:*}: ds1\(W23\) [0-9a-f]+  dW25 ${e##*:} " && okn=$((okn+1)); done
[ $okn = 8 ] && ok "chi38 W23 bits (13,17,26): all 8 re-expanded dW25 values equal the why/ audit table" || bad "chi38 W23 dW25 table" "$okn of 8 match"
expect "chi38 W23: only pattern 111 gives dW25 = 0x20000000 (bits NOT free)" "$o" "pattern 111: .*dW25 20000000 .*<- published" "pattern 111"
expect "chi38 W23: 1 of 8 patterns keeps every later modular difference" "$o" "FLIP result: 1 of 8 patterns keep every later modular difference \(only the published pattern\)" "FLIP result"
o=$($T window --chi chi/chi37.txt --rows 22 36 --event out --np 1024 --mt 4096 --relax R2disputed --hold-from 23 --seeds 5 --quiet)
expect "artifact mode is announced" "$o" "^ARTIFACT MODE \(--hold-from 23\)" "ARTIFACT"
r=$(echo "$o" | grep -oE "R2disputed/cells = [0-9.]+ \+- [0-9.]+" | head -1 | awk '{print $3, $5}')
fcheck "chi37 held-fixed artifact reproduced: W23..W36 held, W22 bits dropped gives ratio ${r% *} +- ${r#* } (the old '+3 bits' = 8)" "(v - 8)^2 <= (${r#* } + 0.05)^2 * 4" "${r% *}"
o=$($T window --chi chi/chi38.txt --rows 23 37 --event out --np 1024 --mt 4096 --relax W23free --seeds 6 --quiet)
r=$(echo "$o" | grep -oE "W23free/cells = [0-9.]+" | head -1 | awk '{print $3}')
[ "$r" = "1.00000" ] && ok "chi38 W23 bits 13,17,26 dropped, real expansion: ratio exactly $r (not free)" || bad "chi38 W23free ratio 1" "$r"
o=$($T window --chi chi/chi38.txt --rows 23 37 --event out --np 1024 --mt 4096 --relax W23free --hold-from 24 --seeds 6 --quiet)
r=$(echo "$o" | grep -oE "W23free/cells = [0-9.]+ \+- [0-9.]+" | head -1 | awk '{print $3, $5}')
fcheck "chi38 held-fixed artifact reproduced: W24..W37 held gives W23free/cells ${r% *} +- ${r#* } (= 8, '+3')" "(v - 8)^2 <= (${r#* } + 0.05)^2 * 4" "${r% *}"
lap

echo "== [K6] row-16 table (r37 proof 6.2, r16.c)"
o=$($T rowtable --chi chi/chi37.txt --row 16 --over W15)
expect "row 16 over the 32 l: 1,052,672 (u,l) pairs, 1,042,240 distinct u, 28 of 32 l nonempty" "$o" "ROWTABLE result: 1052672 \(u, W15\) pairs, 1042240 distinct u, 28 of 32 W15 values nonempty, prefix holds for 32" "ROWTABLE result"
lap

echo "== [X] further exact cross-checks"
o=$($T exact --chi chi/chi37.txt --rows 16 16 --enum W8:set --event state)
expect "chi37 W8 set (cells, two-bit, T8, E4 back) = 12,103,680 = |allg_classes|, all keep rows 4..15" "$o" "members 12103680, y-anchor inconsistent 0" "members"
expect "chi37 W8 set: prefix rows hold for all 12,103,680" "$o" "prefix rows \(< 16\) hold: 12103680" "prefix rows"
if [ -z "$QUICK" ]; then
  o=$($T varcount --chi chi/chi37.txt --word W7)
  expect "chi37 |F7| = 2^26 + 2^20 = 68,157,440" "$o" "68157440 members" "VARCOUNT"
  o=$($T varcount --chi chi/chi38.txt --word W7)
  expect "chi38 |F7| = 287,309,824 (R38M fam38.c)" "$o" "287309824 members" "VARCOUNT"
  o=$($T varcount --chi chi/chi38.txt --word W8)
  expect "chi38 |G| = 2^26 = 67,108,864 (R38M fam38.c)" "$o" "67108864 members" "VARCOUNT"
  o=$($T exact --chi chi/chi38.txt --rows 16 16 --enum E16:all --event state)
  expect "chi38 row 16 on the published head: exactly 32 E16 words (R38M r16enum.py)" "$o" "cells          rows 16..16: 32 " "cells"
  o=$($T exact --chi chi/chi38.txt --rows 19 19 --enum E19:all --event state --relax E19coset)
  expect "chi38 row 19 relaxed (9 E19 value bits dropped) on the published head: 2^26 (job104 measure w19)" "$o" "E19coset +rows 19\.\.19: 67108864 " "E19coset"
fi
lap
echo "== $PASS passed, $FAIL failed ($(( $(date +%s) - T0 )) s)"
[ $FAIL = 0 ]
