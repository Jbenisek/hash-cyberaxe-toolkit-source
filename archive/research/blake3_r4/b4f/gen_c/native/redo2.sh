cd "$(dirname "$0")"
for lim in 1118208 1122304 1126400 1130496 1134592 1138688 1142784; do
  prlimit --as=$lim ./gen_native > o3.bin 2>/dev/null; echo "as=$lim exit $? out $(stat -c %s o3.bin)"
done 2>&1 | grep -v Segm
