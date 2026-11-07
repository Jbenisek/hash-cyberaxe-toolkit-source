cd "$(dirname "$0")"
gcc -Os -static -nostdlib -ffreestanding -fno-builtin -fno-stack-protector -fno-pie -no-pie -Wl,-z,noexecstack -Wno-attributes -o gen_native gen_native.c 2>&1 | head -5
size gen_native
prlimit --data=1048576 --stack=65536 ./gen_native > o.bin 2>/dev/null; echo "data=1048576 stack=65536 exit $? out $(stat -c %s o.bin)"
python3 -B check.py o.bin
prlimit --as=1048576 ./gen_native > o2.bin 2>/dev/null; echo "as=1048576 exit $?"
for lim in 1011712 1015808 1019904 1024000 1032192 1048576 1081344 1114112 1146880 1179648; do
  prlimit --as=$lim ./gen_native > o3.bin 2>/dev/null; echo "as=$lim exit $? out $(stat -c %s o3.bin)"
done
