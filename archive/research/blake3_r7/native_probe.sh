cd "$1" || exit 1
for lim in 1007616 995328 983040 970752 958464 946176 933888 921600; do prlimit --as=$lim ./gen_native > o2.bin 2>/dev/null; echo "as=$lim rc=$?"; done
