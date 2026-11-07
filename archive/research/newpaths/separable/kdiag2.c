/* kdiag2.c - top-level two-list splits of a full-closure guess set S (|S| <= 20):
 * all (U1, U2) with U1 | U2 = S, core C = U1 & U2.  kkey = d(U1) + d(U2) - d(C) - delta(R1 | R2),
 * kpost = delta(R1 | R2) - F.  Prints the maximum kkey and the best two-list cost
 * (cost formula of NOTES.txt with lists = full or partial sides, internal checks iA, iB).
 * Usage: kdiag2 sys setsfile [maxsets]
 */
#include "jtree_core.h"

static double cost2(int c, int a, int b, int iA, int iB, int kkey, int kpost) {
    /* a, b: side dims above core; members = nu + x + y - 32(kkey + kpost) = 64 */
    double best = 1e9;
    for (int nu = 0; nu <= 32 * c && nu <= 200; nu += 4)
        for (int x = 0; x <= 32 * a && x <= 200; x += 2) {
            double y = 64 + 32.0 * (kkey + kpost) - nu - x;
            if (y < 0) y = 0;
            if (y > 32.0 * b) continue;
            double cA = nu + x + 32.0 * iA, cB = nu + y + 32.0 * iB, J = nu + x + y - 32.0 * kkey;
            double m = cA; if (cB > m) m = cB; if (J > m) m = J; if (m < 64) m = 64;
            if (m + 1 < best) best = m + 1;
        }
    return best;
}

int main(int argc, char **argv) {
    load(argv[1]);
    FILE *f = fopen(argv[2], "r"); if (!f) { perror(argv[2]); return 1; }
    long maxsets = argc > 3 ? atol(argv[3]) : 1000000000L;
    char line[4096]; long nsets = 0;
    static long hk[32];
    static M R[1 << 20]; static int d[1 << 20];
    int Sidx[32];
    double gbest = 1e9;
    while (fgets(line, sizeof line, f) && nsets < maxsets) {
        if (strncmp(line, "FULL", 4)) continue;
        char *p = strchr(line, ':'); if (!p) continue; p++;
        int n = 0; char *tok = strtok(p, " \n");
        while (tok) { Sidx[n++] = atoi(tok); tok = strtok(NULL, " \n"); }
        if (n > 20) continue;
        nsets++;
        for (int U = 0; U < (1 << n); U++) {
            M T = 0; for (int j = 0; j < n; j++) if (U & (1 << j)) T |= bit(Sidx[j]);
            R[U] = closure(T); d[U] = delta(R[U]);
        }
        int full = (1 << n) - 1;
        int mk = 0, bu1 = 0, bu2 = 0; double sb = 1e9; int sb1 = 0, sb2 = 0;
        /* enumerate U1 subset of S, U2 = (S - U1) | C with C subset of U1 */
        for (int U1 = 1; U1 < full; U1++) {
            int rest = full ^ U1;
            for (int C = U1; ; C = (C - 1) & U1) {
                int U2 = rest | C;
                if (U2 != full && U1 != C && U2 > U1 - 0) {
                    if ((R[U1] | R[U2]) != R[U1] && (R[U1] | R[U2]) != R[U2]) {
                        int dun = delta(R[U1] | R[U2]);
                        int kkey = d[U1] + d[U2] - d[C] - dun;
                        int kpost = dun - F;
                        if (kkey > mk) { mk = kkey; bu1 = U1; bu2 = U2; }
                        int c = d[C], a = d[U1] - c, b = d[U2] - c;
                        int iA = __builtin_popcount(U1) - d[U1], iB = __builtin_popcount(U2) - d[U2];
                        double lb = 65.0 + 32.0 * kpost; if (33.0 + 16.0 * kkey + 32.0 * kpost > lb) lb = 33.0 + 16.0 * kkey + 32.0 * kpost;
                        if (a > 0 && b > 0 && lb < sb) {
                            double cs = cost2(c, a, b, iA, iB, kkey, kpost);
                            if (cs < sb) { sb = cs; sb1 = U1; sb2 = U2; }
                        }
                    }
                }
                if (C == 0) break;
            }
        }
        hk[mk < 31 ? mk : 31]++;
        if (sb < gbest) gbest = sb;
        printf("set %ld n=%d max kkey %d", nsets, n, mk);
        if (mk > 0) {
            printf("  U1:"); for (int j = 0; j < n; j++) if (bu1 & (1 << j)) printf(" %s", names[Sidx[j]]);
            printf("  U2:"); for (int j = 0; j < n; j++) if (bu2 & (1 << j)) printf(" %s", names[Sidx[j]]);
        }
        printf("  best two-list cost %.0f", sb);
        if (sb < 1e8) {
            printf("  U1:"); for (int j = 0; j < n; j++) if (sb1 & (1 << j)) printf(" %s", names[Sidx[j]]);
            printf("  U2:"); for (int j = 0; j < n; j++) if (sb2 & (1 << j)) printf(" %s", names[Sidx[j]]);
        }
        printf("\n"); fflush(stdout);
    }
    printf("DONE sets=%ld best two-list cost %.0f  histogram of max kkey:", nsets, gbest);
    for (int i = 0; i < 32; i++) if (hk[i]) printf(" %d:%ld", i, hk[i]);
    printf("\n");
    return 0;
}
