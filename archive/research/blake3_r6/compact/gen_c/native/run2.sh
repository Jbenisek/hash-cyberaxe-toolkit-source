cd "$(dirname "$0")"
( /usr/bin/time -v prlimit --data=1048576 --stack=65536 ./gen_native > o.bin ) 2> t.txt; echo "exit $?"; grep -E "Maximum resident" t.txt
python3 -B check.py o.bin
