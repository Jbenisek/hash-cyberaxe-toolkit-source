cd ~/hashsmash/yukon/pos_b3r3pv
grep -rn "nominal-v2" --include=*.py --include=*.json . 2>/dev/null | grep -v "candidates/\|tracks/" | head -12
grep -rn "baseline_improved" --include=*.py . 2>/dev/null | head -8
