#!/usr/bin/env bash
# Which betas of the running count are not done, per slice, and the age of each slice's output.
S="$HOME/hashsmash/pkg7_count"; O="$S/out"; N=${1:-a15}
for i in 0 1 2 3; do
  f="$O/$N.d/raw_$i.out"; [ -f "$f" ] || continue
  done_n=$(grep -c '^DONE' "$f"); all=$(wc -l < "$O/$N.d/slice_$i.lst")
  next=$(awk -v n="$done_n" 'NR == n + 1 {print $1, "k", $2}' "$O/$N.d/slice_$i.lst")
  echo "slice $i: $done_n of $all; in work: ${next:-none}; last output $(( $(date +%s) - $(stat -c %Y "$f") )) s ago; OUTR lines $(grep -c '^OUTR' "$f")"
done
