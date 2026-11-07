#!/bin/bash
# rerun separable's positive control (jtree on the 5-word control system), output into this folder
cd "$(dirname "$0")"
S=../separable
timeout 60 $S/jtree $S/sys_control.txt $S/control_set.txt 2 > jtree_control.out 2>&1
echo "exit $?" >> jtree_control.out
