cd "$(dirname "$0")"
gcc -Os -static -nostdlib -ffreestanding -fno-builtin -fno-stack-protector -fno-pie -no-pie -Wl,-z,noexecstack -Wno-attributes -o gen_native gen_native.c 2>&1 | head -5
size gen_native
for lim in 1048576; do
  echo "--- prlimit --as=$lim"
  /usr/bin/time -v prlimit --as=$lim ./gen_native > out_$lim.bin 2> err_$lim.txt; echo "exit $?"; grep -E "Maximum resident|Exit status" err_$lim.txt; ls -l out_$lim.bin
done
