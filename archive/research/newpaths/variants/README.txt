VARIANTS of the guess-and-determine family question (folder research\newpaths\variants)
Agent "variants" (subagent of the main session), 2026-10-08.  Research only; nothing submitted or posted.
Labels: COMPUTED = produced by a program run here (file named); DERIVED = follows by an argument given in the
files; GUESS = judgement.

READ FIRST
  RESULTS.txt   table of every variant, ranking, what was not tested
  METHOD.txt    model, exact search, split cost formula, two-block CV-list model

PROGRAMS (all small, plain C / Python; run in WSL Ubuntu)
  gd_var.py         word model with options (half 02/13, fixed/outhalf/partial, 64/55 B, CV words unknown)
  gd_two.py         combined two-block model (block 1 free, its CV feeds block 2)
  export_model.py   writes a model file (rules + class representatives) for the C tools; tables t0/t1/t2
  export_partial.py / export_len.py / export_custom.py / export_cv.py / export_two.py / export_b1.py   variants
  gdx.c             exhaustive minimum guess set (canonical DFS over class representatives)
  run_gdx.sh, kmin_q.sh   parallel runners (first k with a solution)
  split.c           core/side meet-in-the-middle analysis of every solution (cost formula in METHOD.txt)
  gdcv.c, stagecheck.c, prep_stage.py   two-block CV-list staging (stagecheck = exact over expanded minimum sets)
  ls.c, ls_all.c    local search (upper bounds for big models)
  ihs2.py + libgd.c implicit-hitting-set lower bounds
  core.c, corex.c   checks inside small cores; 9-guess sets built on self-checked cores
  check_sol.py, struct_sol.py, show_sol.py   independent Python checks of solutions

RESULT FILES (res\)
  kmin.log, summary.log         exhaustive k_min per model
  <model>_k<k>.out              all canonical solutions found (SOL lines = indices into models\<model>.mdl.vars)
  split_*.txt, split_summary.txt  split analysis
  stage_*.out                   CV-list staging
  ls_*.out, ls_job7.txt         local search
  core.txt, corex_*.log         small-core checks
  ihs_*.log                     lower bounds
