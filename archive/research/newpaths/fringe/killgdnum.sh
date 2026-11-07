#!/bin/bash
# stops this folder's gdnum test binaries only
for p in $(pgrep -f '^./gdnum_'); do kill "$p"; echo "killed $p"; done
ps -eo pid,etimes,args | grep -E 'gdnum_|bf rules' | grep -v grep
