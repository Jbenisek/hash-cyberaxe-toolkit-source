#!/bin/bash
# batch.sh LISTFILE : run each line "NAME W TIME KCONF args..." through run2.sh, strictly one after another.
cd "$(dirname "$0")"
while read -r line; do
  [ -z "$line" ] && continue
  case "$line" in \#*) continue;; esac
  echo "=== $line"
  bash ./run2.sh $line
done < "$1"
echo "=== batch done"
