cd "$(dirname "$0")"
gcc -O3 -march=native -Wall -Wno-unused-function -pthread -o cv38 cv38.c -lm || exit 1
date > run.log
./cv38 bij > bij.out 2>&1; echo "bij rc $?" >> run.log
./cv38 cnt 6 3801 --threads 3 > cnt.out 2>&1; echo "cnt rc $?" >> run.log
./cv38 real 30 3802 --threads 3 > real.out 2>&1; echo "real rc $?" >> run.log
date >> run.log; echo DONE >> run.log
