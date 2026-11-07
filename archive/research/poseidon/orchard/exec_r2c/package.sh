#!/bin/bash
# After the counted run: verify, assemble package, prefile_check. (run in WSL; python3)
cd "$(dirname "$0")"; HERE=$PWD
grep -q 'success=1' logs/full_r2.txt || { echo "no collision in log"; exit 3; }
( cd src && R=2 python3 verify_collision.py ../logs/full_r2.txt ) || exit 4
( cd src && size exec_attack > ../logs/size.txt )
( cd src && python3 build_package_r2.py ) > logs/build_package.txt 2>&1 || { tail -15 logs/build_package.txt; exit 5; }
cat logs/build_package.txt
CHK=$HERE/pkg_check; rm -rf "$CHK"; mkdir -p "$CHK/poseidon-orchard-r2"; cp -r "$HERE/pkg_stage/." "$CHK/poseidon-orchard-r2/"; cp "$HERE/submission-note.md" "$CHK/submission-note.md"
python3 ../../../launch/prefile_check.py "$CHK" > logs/prefile.txt 2>&1
tail -1 logs/prefile.txt; grep '^FAIL' logs/prefile.txt | cut -c1-200
