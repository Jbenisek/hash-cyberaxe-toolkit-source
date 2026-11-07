#!/bin/bash
# usage: run_many.sh <timeout_s> <cnf>...   runs kissat on each in parallel; prints one line per file
cd "$(dirname "$0")"
to=$1; shift
for f in "$@"; do
  ( timeout "$to" kissat -q "$f" > "${f%.cnf}.out"; echo "$f exit=$?" >> run_many.log ) &
done
wait
