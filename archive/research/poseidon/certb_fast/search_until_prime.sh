#!/bin/bash
# runs centres one at a time on the GPU; stops at the first leftover of PRIME degree in (19531, 39059]
cd "$(dirname "$0")"; list="$1"; od="${2:-out/search1}"; mkdir -p "$od"; i=0
isprime(){ python3 -c "import sys;n=int(sys.argv[1]);print(int(n>1 and all(n%q for q in range(2,int(n**.5)+1))))" "$1"; }
while read -r c; do i=$((i+1))
  nice -n 10 ./certb_fast ddf --F "${F_BIN:-tests/data/F_j0.bin}" --center "$c" --out "$od/c$i" > "$od/c$i.log" 2>&1
  r=$(grep -o '"residual_degree":[0-9]*' "$od/c$i.log" | tail -1 | cut -d: -f2); ab=$(grep -o '"aborted_early":[a-z]*' "$od/c$i.log" | tail -1 | cut -d: -f2)
  pr=0; [ -n "$r" ] && [ "$ab" != "true" ] && [ "$r" -gt 19531 ] && [ "$r" -le 39059 ] && pr=$(isprime "$r")
  echo "$(date +%H:%M:%S) c$i residual=$r aborted=$ab prime=$pr centre=$c" >> "$od/progress.txt"
  [ "$pr" = "1" ] && { echo "WITNESS c$i centre=$c l=$r" >> "$od/progress.txt"; echo "$c" > "$od/WITNESS_CENTRE.txt"; break; }
done < "$list"
echo DONE >> "$od/progress.txt"
