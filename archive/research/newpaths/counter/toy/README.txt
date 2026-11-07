counter\toy: scaled-down end-to-end test of the chunk-counter lever (W = 8). Research only; nothing submitted.
Results: TOY_RESULT.txt. Tags there: COMPUTED (run here), DERIVED (argued), GUESS.

FILES
  toy.h, tl_lines.inc, sets_w8.txt   unchanged copies from astra-jobs\server_tasks_2026-10-06\task5_small_h8
                                     (toy hash, two-level trial lines, the 48 constant sets with exact sumper)
  ctr_toy.c                          the program (modes mass / check / run / treetest); built in WSL with
                                     g++ -O3 -march=native -x c++ -DWBITS=8 -w -o ~/ctr_toy_bin/ctr_toy8 ctr_toy.c -lm
  verify_tree.py                     independent Python toy tree hash (selftest at W=32 vs hash-smash\verifier\blake3.py;
                                     treetest vs the C tree hash; hits: rehash every collision as full messages)
  summarize.py -> summary.txt        found vs predicted, work per collision, measured gain
  mass_set<i>.txt, massmat_set<i>.txt, mass_summary.txt   exact counts per set (sumper, mass per beta, mass[member][d1])
  gain_stats_w8.txt, joint_gain_w8.txt                     toy T1 factors over 48 sets; joint (member, beta) choice
  check_w8.txt                       construction checks (sets 0..7, 3000 trials each, both arrangements)
  treetest_w8.txt                    40 random messages (up to 5 chunks) with their C tree hashes
  verify_hits.txt, work_lines.txt    Python re-hash of all 372 collisions; t statistics and derived line counts
  jobs.txt, worker.sh, start_all.sh  the counted runs (4 background workers, 90-min limit); my_pids.txt = PIDs
                                     (all finished); jobs_extra.txt = the 24 control runs appended later
  out\<tag>_set<i>_r<first>.txt      raw output (RUN, HIT, PART lines). NOTE: jobs.txt was written with CRLF, so the
                                     tag in the file names ends in a CR, shown by Windows as U+F00D (harmless;
                                     summarize.py strips it).
  build_check.sh, check.sh, mass1.sh, mass_all.sh, speed.sh, ps.sh   helper scripts

COMMANDS (from PowerShell)
  wsl -d Ubuntu -- bash ./research/newpaths/counter/toy/mass_all.sh
  wsl -d Ubuntu -- bash ./research/newpaths/counter/toy/check.sh
  wsl -d Ubuntu -- bash ./research/newpaths/counter/toy/start_all.sh
  python -B verify_tree.py selftest ; python -B verify_tree.py treetest treetest_w8.txt
  python -B verify_tree.py hits out\*.txt ; python -B summarize.py   (set PYTHONIOENCODING=utf-8)
