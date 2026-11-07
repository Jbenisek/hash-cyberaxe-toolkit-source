#!/usr/bin/env bash
# Reviewer: the statistics of cadical's internal checkers from the probe of math_probe2.sh.
grep -A4 -E 'checker statistics' "$HOME/hashsmash/pkg5-review-math/probe.out" | grep -vE '^c *$|^--' | cut -c1-100 | head -10
