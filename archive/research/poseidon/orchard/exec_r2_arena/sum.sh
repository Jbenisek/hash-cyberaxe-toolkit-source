for d in /root/arena_r2/67108864 /root/arena_r2/*pm*k /root/arena_r2/*pack*; do echo "== $d"; grep -E "^trial|digest" $d/run.txt; done
