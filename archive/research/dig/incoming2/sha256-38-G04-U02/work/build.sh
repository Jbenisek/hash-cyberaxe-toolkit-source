cd "$(dirname "$0")"
gcc -O3 -march=native -Wall -Wno-unused-function -pthread -o cv38 cv38.c -lm
./cv38 val > val.out; cat val.out
./cv38 dep 20000 > dep.out; cat dep.out
./cv38 dcv > dcv.out; cat dcv.out
./cv38 f7 --threads 3 > f7.out; cat f7.out
