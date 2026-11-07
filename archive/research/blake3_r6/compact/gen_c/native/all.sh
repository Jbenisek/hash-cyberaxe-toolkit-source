cd "$(dirname "$0")"
gcc -Os -static -nostdlib -ffreestanding -fno-builtin -fno-stack-protector -fno-pie -no-pie -Wl,-z,noexecstack -Wno-attributes -o gen_native gen_native.c 2>&1 | head -5
size gen_native
nice -n 19 bash bisect.sh
nice -n 19 bash run2.sh
prlimit --data=1048576 --stack=65536 ./gen_native > o.bin; python3 -B check.py o.bin
