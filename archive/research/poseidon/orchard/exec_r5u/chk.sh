cd "$(dirname "$0")"; W=historical-sources/~~Projects/~HashSmash/workspace
python3 -B $W/research/launch/prefile_check.py $PWD/pkg_fin_check > logs/fin_prefile.txt 2>&1; tail -3 logs/fin_prefile.txt; grep '^FAIL' logs/fin_prefile.txt | cut -c1-250
python3 -B $W/research/tools/rulecheck/rulecheck.py $PWD/pkg_fin_check 2>&1 | tail -16
