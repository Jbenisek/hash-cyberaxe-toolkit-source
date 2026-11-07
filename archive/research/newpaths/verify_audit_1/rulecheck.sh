#!/bin/bash
cd "$(dirname "$0")"
echo "plain, no rules:";   ./lk2 sys_fixed_plain.txt 2 0 1 plain desc - | cut -c60-300
echo "plain, gen rules:";  ./lk2 sys_fixed_plain.txt 2 0 1 plain desc ../audit/rules_fixed_len64_gen.txt | cut -c60-300
echo "plain, pair rules:"; ./lk2 sys_fixed_plain.txt 2 0 1 plain desc ../audit/rules_fixed_len64_pair.txt | cut -c60-300
echo "look, no rules:";    ./lk2 sys_fixed_plain.txt 2 0 1 look desc - | cut -c60-300
echo "look, gen rules:";   ./lk2 sys_fixed_plain.txt 2 0 1 look desc ../audit/rules_fixed_len64_gen.txt | cut -c60-300
