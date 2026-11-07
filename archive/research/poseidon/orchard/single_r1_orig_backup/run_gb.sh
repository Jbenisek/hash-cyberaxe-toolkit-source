cd "$(dirname "$0")"
gcc -O3 -march=native -Wall -Wno-unused-function -Wno-unused-variable -Wno-unused-parameter -Wno-unused-but-set-variable -o gcdbound gcdbound.c common.c ntt.c poly.c lean.c line.c split.c pallas.c -lm 2>&1 | head -30
nice -n 10 ./gcdbound "$@"
