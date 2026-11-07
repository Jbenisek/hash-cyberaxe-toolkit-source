cd "$(dirname "$0")"
./build.sh test_hgcd 2>&1 | head -30
for args in "300 3 299" "1000 5 999" "1000 5 10" "1000 5 500" "1000 5 6" "3000 7 2999" "3000 0 100" "3000 10 600"; do nice -n 10 ./test_hgcd $args 1; done
