#!/bin/bash
# positive control: separable's own jtree on a synthetic 8-guess, F=4, 4-check system with keys (2,2) at two levels
cd "$(dirname "$0")"
timeout 100 ../separable/jtree ctrl8.txt ctrl8_set.txt 3 200
echo "== same set, cores up to 0 only"
timeout 100 ../separable/jtree ctrl8.txt ctrl8_set.txt 0 200
