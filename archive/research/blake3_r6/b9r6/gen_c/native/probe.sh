cd "$(dirname "$0")"
for lim in 1060864 1081344 1114112 1179648 1310720 1572864; do
  prlimit --as=$lim ./gen_native > o.bin 2>/dev/null; echo "as=$lim exit $? out $(stat -c %s o.bin)"
done
prlimit --data=1048576 ./gen_native > o.bin 2>/dev/null; echo "data=1048576 exit $? out $(stat -c %s o.bin)"
prlimit --data=1048576 --stack=65536 ./gen_native > o.bin 2>/dev/null; echo "data=1048576 stack=65536 exit $? out $(stat -c %s o.bin)"
cat /proc/self/maps | head -3
