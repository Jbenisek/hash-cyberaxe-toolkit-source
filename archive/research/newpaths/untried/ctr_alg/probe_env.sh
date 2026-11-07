#!/bin/bash
# probe_env.sh - list SAT solvers and Python modules available in WSL (read-only probe)
for b in kissat cadical cryptominisat5 cryptominisat minisat glucose; do
  printf '%s: ' "$b"; command -v "$b" || echo none
done
for d in "$HOME/bin" "$HOME/.local/bin" /opt /usr/local/bin; do
  ls -1 "$d" 2>/dev/null | grep -iE 'kissat|cadical|crypto|minisat|glucose' | sed "s|^|$d/|"
done
python3 --version
python3 - <<'EOF'
import importlib.util as u
print({m: bool(u.find_spec(m)) for m in ['pysat', 'pycryptosat', 'numpy']})
EOF
nproc
