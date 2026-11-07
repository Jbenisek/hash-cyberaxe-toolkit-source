#!/bin/bash
# probe_opts.sh - option names for statistics, time limits, Gauss-Jordan (read-only)
echo "== kissat"; kissat --help 2>&1 | grep -iE 'statist|--time|seed|quiet|verbose|witness|ticks' | head -n 20
echo "== cadical"; cadical --help 2>&1 | grep -iE 'stat|-t |seed|quiet|witness|verbose' | head -n 20
echo "== cms"; cryptominisat5 --help 2>&1 | grep -iE 'gauss|matrix|xor|maxtime|verb|seed|printsol' | head -n 40
