cd ~/hashsmash/yukon/pos_b3r3pv
grep -rn "reference_operation_cost" --include=*.py --include=*.json --include=*.md . 2>/dev/null | grep -v "^./tracks\|candidates" | head -40
echo ----
grep -rn "638" --include=*.py --include=*.json . 2>/dev/null | grep -v candidates | head
