/* kdiag.c - for guess sets S (no core), list the splits S = U1 + U2 (both nonempty) and print
 * d(U1), d(U2), kkey (join-key conditions between cl(U1) and cl(U2)) and kpost, plus the max kkey
 * over all sub-pairs (U1, U2 disjoint subsets, not necessarily covering S).
 * Usage: kdiag sys setsfile [maxsets]
 */
#include "jtree_core.h"

int main(int argc, char **argv) {
    load(argv[1]);
    FILE *f = fopen(argv[2], "r"); if (!f) { perror(argv[2]); return 1; }
    long maxsets = argc > 3 ? atol(argv[3]) : 1000000000L;
    char line[4096]; long nsets = 0;
    static long hk[16];
    int Sidx[16];
    while (fgets(line, sizeof line, f) && nsets < maxsets) {
        if (strncmp(line, "FULL", 4)) continue;
        char *p = strchr(line, ':'); if (!p) continue; p++;
        int n = 0; char *tok = strtok(p, " \n");
        while (tok) { Sidx[n++] = atoi(tok); tok = strtok(NULL, " \n"); }
        nsets++;
        static M R[1 << 14]; static int d[1 << 14];
        for (int U = 0; U < (1 << n); U++) {
            M T = 0; for (int j = 0; j < n; j++) if (U & (1 << j)) T |= bit(Sidx[j]);
            R[U] = closure(T); d[U] = delta(R[U]);
        }
        /* all pairs of subsets (U1, U2), shared part C = U1 & U2 acts as the core:
         * kkey = d(U1) + d(U2) - d(C) - delta(R1 | R2) */
        int mk = 0, bu1 = 0, bu2 = 0;
        for (int U1 = 1; U1 < (1 << n); U1++) {
            for (int U2 = 1; U2 <= U1; U2++) {
                if ((U1 | U2) == U1 || (U1 | U2) == U2) continue;   /* one contains the other: no join */
                if ((R[U1] | R[U2]) == R[U1] || (R[U1] | R[U2]) == R[U2]) continue;
                int C = U1 & U2;
                int kkey = d[U1] + d[U2] - d[C] - delta(R[U1] | R[U2]);
                if (kkey > mk) { mk = kkey; bu1 = U1; bu2 = U2; }
            }
        }
        hk[mk]++;
        if (mk >= 2 || nsets <= 3) {
            printf("set %ld max kkey %d  U1:", nsets, mk);
            for (int j = 0; j < n; j++) if (bu1 & (1 << j)) printf(" %s", names[Sidx[j]]);
            printf("  U2:"); for (int j = 0; j < n; j++) if (bu2 & (1 << j)) printf(" %s", names[Sidx[j]]);
            printf("  |R1|=%d |R2|=%d d1=%d d2=%d\n", pc(R[bu1]), pc(R[bu2]), d[bu1], d[bu2]);
        }
    }
    printf("DONE sets=%ld  histogram of max kkey:", nsets);
    for (int i = 0; i < 16; i++) if (hk[i]) printf(" %d:%ld", i, hk[i]);
    printf("\n");
    return 0;
}
