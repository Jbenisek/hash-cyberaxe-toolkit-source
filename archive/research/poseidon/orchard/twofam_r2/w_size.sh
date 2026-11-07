#!/bin/bash
cd "$(dirname "$0")"
bash build.sh twofam 2>&1 | grep -i " error"
size twofam > logs/size.txt; cat logs/size.txt
