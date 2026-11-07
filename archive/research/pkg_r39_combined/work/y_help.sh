#!/usr/bin/env bash
export PATH="$HOME/.local/bin:$HOME/.bun/bin:$PATH" NO_COLOR=1
yukon --help 2>&1 | head -40
yukon reset --help 2>&1 | head -30
yukon clone --help 2>&1 | head -30
ls ~/hashsmash/yukon | head -50
