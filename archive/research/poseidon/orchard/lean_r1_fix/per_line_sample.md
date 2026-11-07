# Per-line sample
binary lean_attack, args "1 1 seed j 1", seeds 100000.., j=seed%3

line 0: 18/60 = 0.300, Wilson95 lower 0.199
line 1: 19/60 = 0.317, Wilson95 lower 0.213
line 2: 20/60 = 0.333, Wilson95 lower 0.227
q_min = 0.1990
C=2: 1-(1-q)^C = 0.358
C=4: 1-(1-q)^C = 0.588
C=6: 1-(1-q)^C = 0.736
smallest C clearing 0.39: 3
