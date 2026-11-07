#!/bin/bash
cd "$(dirname "$0")"
for a in 0x42ec1c 0x432b23 0x433096 0x434483 0x432b10 0x433062 0x433074 0x433087; do echo "== $a"; addr2line -f -i -e dtest_mt $a | paste - - | sed 's#historical-sources/.*/single_r1_mem/##'; done
