#!/bin/bash
# kill only my own processes whose command line matches the given pattern (never other jobs)
pat="$1"
for p in $(pgrep -f "$pat"); do
  if [ "$p" != "$$" ] && ps -o args= -p "$p" | grep -q "^\(timeout [0-9]* \)\?\./\(fullsets\|split\|jtree\|kdiag\|lsearch\)"; then
    kill "$p" && echo "killed $p: $(ps -o args= -p $p 2>/dev/null)"
  fi
done
