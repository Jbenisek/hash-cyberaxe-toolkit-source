# usage: native_json.sh <gen_c/native dir>   builds gen_native, runs it under prlimit --as=1048576 and --as=1007616, writes native.json
cd "$1" || exit 1
gcc -Os -static -nostdlib -ffreestanding -fno-builtin -fno-stack-protector -fno-pie -no-pie -Wl,-z,noexecstack -Wno-attributes -o gen_native gen_native.c 2>&1 | head -5
read TXT DATA BSS REST < <(size gen_native | tail -1)
prlimit --as=1048576 ./gen_native > o.bin 2>/dev/null; RC1=$?
OK=$(python3 -B check.py o.bin | grep -c "sha256 equal to the Python reference: True")
prlimit --as=1007616 ./gen_native > o2.bin 2>/dev/null; RC2=$?
echo "rc as=1048576: $RC1  identical-line-count: $OK  rc as=1007616: $RC2  text $TXT data $DATA bss $BSS"
if [ "$RC1" = 0 ] && [ "$OK" = 1 ] && [ "$RC2" != 0 ]; then
  python3 - <<PY
import json
json.dump({"identical": True, "bss": $BSS, "text": $TXT, "as_ok": 1048576, "as_fail": 1007616, "data_cap": 1048576}, open("native.json", "w"))
print(open("native.json").read())
PY
fi
