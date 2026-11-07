cd "$(dirname "$0")"
rm -f gen_native o.bin o2.bin out_*.bin
bash build_run.sh
bash run2.sh
bash bisect.sh
