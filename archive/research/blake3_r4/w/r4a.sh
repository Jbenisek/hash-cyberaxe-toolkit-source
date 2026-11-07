cd ~/hashsmash/yukon/pos_b3r3pv
ls -la; ls -la pareto/candidates; git -C pareto log --oneline 2>&1 | head -3; git log --oneline 2>&1 | head -3
cd pareto
diff <(python3 -m json.tool target-profiles/blake3-r3-prefix-v1.json) <(python3 -m json.tool target-profiles/blake3-r4-prefix-v1.json)
cat target-profiles/blake3-r4-prefix-v1.json
