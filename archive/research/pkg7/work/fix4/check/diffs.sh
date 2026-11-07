#!/usr/bin/env bash

# Publication root: stable even when this driver changes working directories.
if [ -z "${HASHCYBERAXE_WORKSPACE:-}" ]; then
  _hca_here=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
  while [ ! -d "$_hca_here/research" ] && [ "$_hca_here" != / ]; do _hca_here=$(dirname -- "$_hca_here"); done
  HASHCYBERAXE_WORKSPACE=$_hca_here
fi
export HASHCYBERAXE_WORKSPACE
# FIX4 check: write diffs prev -> present into check/. Read-only otherwise.
P="${HASHCYBERAXE_WORKSPACE}/research/pkg7"
V="$P/work/fix4/prev"; C="$P/work/fix4/check"
diff -u "$V/blake3-r2/proof.md" "$P/blake3-r2/proof.md" > "$C/d_proof.diff"
diff -u "$V/blake3-r2/claim.json" "$P/blake3-r2/claim.json" > "$C/d_claim.diff"
diff -u "$V/submission-note-r2.md" "$P/submission-note-r2.md" > "$C/d_note.diff"
diff -u "$V/FILE_STEPS.md" "$P/FILE_STEPS.md" > "$C/d_filesteps.diff"
for f in claim.json note.md proof_evidence.md proof_head.md; do diff -u "$V/src/$f" "$P/src/$f" > "$C/d_src_$f.diff"; done
# claim.json fields other than limitations: compare parsed JSON with limitation strings removed
python3 - "$V/blake3-r2/claim.json" "$P/blake3-r2/claim.json" > "$C/d_claim_fields.txt" <<'EOF'
import json,sys
a=json.load(open(sys.argv[1])); b=json.load(open(sys.argv[2]))
def walk(x,y,path):
    if type(x)!=type(y): print("TYPE",path); return
    if isinstance(x,dict):
        for k in sorted(set(x)|set(y)):
            if k not in x or k not in y: print("KEY", path+"/"+k, k in x, k in y); continue
            walk(x[k],y[k],path+"/"+k)
    elif isinstance(x,list):
        if len(x)!=len(y): print("LEN",path,len(x),len(y))
        for i,(p,q) in enumerate(zip(x,y)): walk(p,q,path+"[%d]"%i)
    elif x!=y: print("DIFF",path,len(str(x)),len(str(y)))
walk(a,b,"")
print("state",b.get("submission_state"),"time_log2",b.get("time_log2"))
EOF
for f in "$C"/d_*; do echo "$(wc -l < "$f") $(basename "$f")"; done
