#!/usr/bin/env bash
# Reviewer: which proof options the installed solvers have (read-only probe).
cadical --version | head -1
cadical --help 2>&1 | grep -iE -- '--check|--lrat|--frat|--plain|--binary' | cut -c1-110 | head -8
kissat --version | head -1
