#!/bin/bash
cd "$(dirname "$0")"
for t in twofam test_split calib; do bash build.sh $t 2>&1 | grep -v "warning\|~\|^ *[0-9]* |" ; done
echo built
