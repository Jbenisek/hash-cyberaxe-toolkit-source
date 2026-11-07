cd "$(dirname "$0")"
cat head.inc body.c > scan.c
S=../../../../tools/traillab/src
gcc -O3 -march=native -Wall -Wno-unused-parameter -Wno-unused-function -Wno-misleading-indentation -pthread -o scan scan.c $S/traillab.c $S/smc.c $S/diff.c -lm 2>&1 | head -30
