cd "$(dirname "$0")"
lo=65536; hi=1048576
while [ $((hi-lo)) -gt 4096 ]; do
  mid=$(( (lo+hi)/2/4096*4096 ))
  if prlimit --as=$mid ./gen_native > o2.bin 2>/dev/null && [ "$(stat -c %s o2.bin)" -gt 1000 ]; then hi=$mid; else lo=$mid; fi
done
echo ok=$hi fail=$lo
