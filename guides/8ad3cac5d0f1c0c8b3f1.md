# State of the long self-test runs of tools/selftest_big.sh, and a way to stop them. Research helper, not submitted.

Source: `research/pkg9/pkg/tools/selftest_big_launch.sh`

Public SHA-256: `51bb5bb7aa5870f5522994af3325c7bf0a5fdcd683d6e3c264fca20091dafb7b`

## Purpose recorded in the source

State of the long self-test runs of tools/selftest_big.sh, and a way to stop them. Research helper, not submitted.

  wsl -d Ubuntu -- bash './research/pkg6/tools/selftest_big_launch.sh' status
  wsl -d Ubuntu -- bash './research/pkg6/tools/selftest_big_launch.sh' stop

How the runs of 2026-10-06 were started: a run of 1,000,000 batches takes about half an hour per rule, and on
this machine the processes of a "wsl ... &" end when the wsl client that started them ends (setsid and nohup did
not keep them). They were started from PowerShell as a process of their own:
  Start-Process -FilePath wsl.exe -WindowStyle Hidden -ArgumentList '-d','Ubuntu','--','bash',
    './research/pkg6/tools/selftest_big.sh','1000000','61','4','5','6'
A run that is stopped leaves an evidence file whose first line ends with "exit 143"; such a file is not evidence
(tools/rule_figures.py and the data module use a file only with "exit 0").

## Source inspection and available execution evidence

static-source-review; not-replayed-for-publication.

A run budget is not specified in this guide. Check loop bounds, worker counts and memory requirements before choosing an experiment size.

## Read alongside

- research/pkg9/pkg/tools/proof_lines_check.py
- research/pkg9/pkg/tools/proof_lines_pkg7.py

## Failure modes

- Missing historical dependencies or input files.
- Domain or target parameters may differ from the intended experiment.
- Publication redactions can change executable strings; compare source and public digests.
