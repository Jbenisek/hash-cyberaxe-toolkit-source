#!/usr/bin/env bash
# Load of the WSL machine and the processes of this job (research/pkg7, step PROGRAM). Prints a few lines.
echo "load $(cut -d' ' -f1-3 /proc/loadavg), processors $(nproc), python3 $(python3 --version 2>&1 | cut -d' ' -f2)"
echo "python processes of pkg7run: $(pgrep -af 'pkg7run|research/pkg7/' | grep -c python)"
pgrep -af 'pkg7run|research/pkg7/' | grep python | cut -c1-150 | head -6
ls "$HOME/hashsmash/pkg7run" 2>/dev/null | head -8
