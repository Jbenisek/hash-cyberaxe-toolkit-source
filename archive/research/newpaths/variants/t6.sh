#!/bin/bash
cd "$(dirname "$0")"
for m in fixed_02_64_t0 fixed_13_64_t0 fixed_02_64_t1 fixed_13_64_t1; do echo "== $m"; /usr/bin/time -f "%e s" timeout 100 ./gdx models/$m.mdl 6 0 1 3 | tail -4; done
