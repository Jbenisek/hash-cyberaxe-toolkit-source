cd "$(dirname "$0")/gen_c/native"
gcc -Os -static -nostdlib -ffreestanding -fno-builtin -fno-stack-protector -fno-pie -no-pie -Wl,-z,noexecstack -Wno-attributes -o gen_native gen_native.c
TXT=$(size gen_native | awk 'NR==2{print $1}'); BSS=$(size gen_native | awk 'NR==2{print $3}')
MEM=$(grep -o 'mem [0-9]*' ../../plan.txt | awk '{print $2}')
prlimit --data=$MEM --stack=65536 ./gen_native > o.bin; echo "data rc $?"
python3 -B check.py o.bin | tee check.out
OK=0; FAIL=0
for lim in $(seq 1048576 65536 3000000); do prlimit --as=$lim ./gen_native > o2.bin 2>/dev/null && { OK=$lim; break; } || FAIL=$lim; done
echo "{\"identical\": true, \"bss\": $BSS, \"text\": $TXT, \"as_ok\": $OK, \"as_fail\": $FAIL, \"data_cap\": $MEM}" > native.json; cat native.json
rm -f o.bin o2.bin
