#!/bin/bash
cd "$(dirname "$0")"
kill 1222338 1222340 1225707 2>/dev/null
gcc -O3 -march=native -Wall -Wno-unused -o certrun certrun.c common.c ntt.c poly.c lean.c line.c split.c pallas.c -lm 2>&1 | grep -i "error"
cat > run_cert.sh <<'EOT'
#!/bin/bash
cd "$(dirname "$0")"
nice -n 10 ./certrun 2 $1 > logs/cert_r2_$1.txt 2>&1
echo "EXIT $?" >> logs/cert_r2_$1.txt
EOT
for s in 501 502 503 504; do setsid nohup bash run_cert.sh $s > /dev/null 2>&1 < /dev/null & done
sleep 2; pgrep -a "certrun"
