/* verify_audit_1 split2: best two-list join cost for a given cover, generous version.
   For every assignment of the guesses to core/A/B:
     Kc = close(core), KA = close(core+A), KB = close(core+B)   (close = plain, + look unless PLAIN is set)
     join conditions jc = shared words (in KA and KB, not in Kc: computed from both sides, equality is a 32-bit
       condition) + equations fully inside KA u KB but inside neither + post-join SEPARABLE checks, found by typed
       propagation from J = KA u KB: a derived word is A / B if all inputs are (core or) one side, SP if the equation is
       a modular sum and all inputs are A/B/SP, SX if xor-rotation and all inputs A/B/SX, else M (mixed, per pair);
       a check is separable (a join condition) when its type set fits the same rule.  Look acceptances after the join
       give M words (their per-candidate search is taken as free, as in the claim).
     internal checks iA, iB = filters inside one side; post filters pf = non-separable checks (minus acceptance pins).
   Cost (brief-rule units: 1 per list element built and per join candidate; the /430 word-op discount is NOT applied):
     choose bits x <= 32|A|, y <= 32|B| enumerated per side, n <= 32|core| bits of core values;
     members = n + x + y - 32(iA+iB+jc+pf) >= 64;   cost = n + max(x, y, x + y - 32(iA+iB+jc)), then max with 64.
   Prints the best cost exponent per cover.  usage: [PLAIN=1] split2 <sysfile>  < sets */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdint.h>

#define MAXV 128
#define MAXE 160
typedef struct { uint64_t w[2]; } bs;
static int nv, ne, LOOK = 1, BAL = 0;
static char names[MAXV][32];
static bs em[MAXE];
static int ev[MAXE][4], nev[MAXE];
static inline int has(const bs *k, int v) { return (k->w[v >> 6] >> (v & 63)) & 1; }
static inline void setb(bs *k, int v) { k->w[v >> 6] |= 1ULL << (v & 63); }
static inline int pc(const bs *k) { return __builtin_popcountll(k->w[0]) + __builtin_popcountll(k->w[1]); }
static inline int sub(const bs *a, const bs *k) { return !((a->w[0] & ~k->w[0]) | (a->w[1] & ~k->w[1])); }
static void plc(bs *K) {
    int ch = 1;
    while (ch) { ch = 0;
        for (int e = 0; e < ne; e++) { uint64_t u0 = em[e].w[0] & ~K->w[0], u1 = em[e].w[1] & ~K->w[1];
            if (__builtin_popcountll(u0) + __builtin_popcountll(u1) == 1) { K->w[0] |= u0; K->w[1] |= u1; ch = 1; } } }
}
static int ncov(const bs *K) { int c = 0; for (int e = 0; e < ne; e++) c += sub(&em[e], K); return c; }
static int nacc;
static int lookone(bs *K) {   /* one look acceptance; returns z or -1 */
    int c0 = ncov(K), n0 = pc(K);
    for (int z = 0; z < nv; z++) { if (has(K, z)) continue;
        bs T = *K; setb(&T, z); plc(&T);
        if (ncov(&T) - c0 >= pc(&T) - n0) return z; }
    return -1;
}
static void lclose(bs *K) { plc(K); if (!LOOK) return; int z; while ((z = lookone(K)) >= 0) { setb(K, z); plc(K); nacc++; } }

enum { TC = 0, TA = 1, TB = 2, TSP = 3, TSX = 4, TM = 5 };
static int isadd(int e) { return (e % 8) % 2 == 0; }   /* per G: a1 d1 c1 b1 a2 d2 c2 b2 -> add xor add xor ... */
static int restype(int e, int *ts, int n) {
    int m = 0; for (int i = 0; i < n; i++) m |= 1 << ts[i];
    m &= ~(1 << TC);
    if (!(m & ~(1 << TA))) return m ? TA : TC;
    if (!(m & ~(1 << TB))) return TB;
    int okmask = isadd(e) ? ((1 << TA) | (1 << TB) | (1 << TSP)) : ((1 << TA) | (1 << TB) | (1 << TSX));
    if (!(m & ~okmask)) return isadd(e) ? TSP : TSX;
    return TM;
}

static double bestcost(int a, int b, int c, int iA, int iB, int jc, int pf) {
    double best = 1e9; int I = 32 * (iA + iB + jc), P = 32 * pf;
    for (int x = 0; x <= 32 * a; x += 2) for (int y = 0; y <= 32 * b; y += 2) {
        int n = 64 + I + P - x - y; if (n < 0) n = 0; if (n > 32 * c) continue;
        int mx = x > y ? x : y; if (x + y - I > mx) mx = x + y - I;
        double cost = n + mx; if (cost < 64) cost = 64;
        if (cost < best) best = cost;
    }
    return best;
}

int main(int argc, char **argv) {
    if (getenv("PLAIN")) LOOK = 0;
    if (getenv("BAL")) BAL = 1;
    if (argc > 2 && !strcmp(argv[2], "costtest")) {
        printf("a3 b3 c1 jc3 pf0 -> %.0f (expect 80)\n", bestcost(3, 3, 1, 0, 0, 3, 0));
        printf("a2 b2 c2 jc2 pf0 -> %.0f (expect 64)\n", bestcost(2, 2, 2, 0, 0, 2, 0));
        printf("a3 b4 c0 jc0 pf3 -> %.0f (expect 160)\n", bestcost(3, 4, 0, 0, 0, 0, 3));
        printf("a3 b3 c2 jc4 pf0 -> %.0f (expect 96)\n", bestcost(3, 3, 2, 0, 0, 4, 0));
        printf("a2 b4 c1 jc3 pf0 -> %.0f (expect 96)\n", bestcost(2, 4, 1, 0, 0, 3, 0));
        printf("a3 b3 c1 jc2 pf1 -> %.0f\n", bestcost(3, 3, 1, 0, 0, 2, 1));
        return 0;
    }
    FILE *f = fopen(argv[1], "r"); int nr; char line[8192];
    if (!f || fscanf(f, "%d %d %d", &nv, &ne, &nr) != 3) return 1;
    for (int i = 0; i < nv; i++) if (fscanf(f, "%31s", names[i]) != 1) return 1;
    if (!fgets(line, sizeof line, f)) return 1;
    for (int e = 0; e < ne; e++) { if (!fgets(line, sizeof line, f)) return 1; char *q = line; int v, n;
        while (sscanf(q, "%d%n", &v, &n) == 1) { setb(&em[e], v); ev[e][nev[e]++] = v; q += n; } }
    fclose(f);
    int nsets = 0, gmaxjc = 0; double overall = 1e9; int hist[200] = {0};
    while (fgets(line, sizeof line, stdin)) {
        int G[16], g = 0;
        for (char *tok = strtok(line, " \t\r\n"); tok; tok = strtok(NULL, " \t\r\n")) {
            int v = -1; for (int i = 0; i < nv; i++) if (!strcmp(names[i], tok)) v = i;
            if (v < 0) { printf("unknown %s\n", tok); return 1; } G[g++] = v; }
        if (!g) continue;
        bs K = {{0, 0}}; lclose(&K); for (int i = 0; i < g; i++) { setb(&K, G[i]); lclose(&K); }
        if (pc(&K) != nv) { printf("not a cover (%d/%d)\n", pc(&K), nv); continue; }
        nsets++;
        int pw = 1; for (int i = 0; i < g; i++) pw *= 3;
        double best = 1e9; char desc[600] = ""; int bestjc = -1, maxjc = 0;
        for (int asg = 0; asg < pw; asg++) {
            int x = asg, role[16], na = 0, nb = 0, nc = 0;
            for (int i = 0; i < g; i++) { role[i] = x % 3; x /= 3; if (role[i] == 1) na++; else if (role[i] == 2) nb++; else nc++; }
            if (na == 0 || nb == 0 || na > nb) continue;
            if (BAL && (na < 3 || nb < 3)) continue;
            bs Kc = {{0, 0}}; lclose(&Kc); for (int i = 0; i < g; i++) if (role[i] == 0) { setb(&Kc, G[i]); lclose(&Kc); }
            bs KA = Kc, KB = Kc;
            for (int i = 0; i < g; i++) if (role[i] == 1) { setb(&KA, G[i]); lclose(&KA); }
            for (int i = 0; i < g; i++) if (role[i] == 2) { setb(&KB, G[i]); lclose(&KB); }
            int iA = ncov(&KA) - ncov(&Kc) - pc(&KA) + pc(&Kc) + na;
            int iB = ncov(&KB) - ncov(&Kc) - pc(&KB) + pc(&Kc) + nb;
            int type[MAXV]; bs J = {{KA.w[0] | KB.w[0], KA.w[1] | KB.w[1]}}; bs J0 = J;
            int shared = 0;
            for (int v = 0; v < nv; v++) {
                if (has(&Kc, v)) type[v] = TC;
                else if (has(&KA, v) && has(&KB, v)) { type[v] = TA; shared++; }
                else if (has(&KA, v)) type[v] = TA;
                else if (has(&KB, v)) type[v] = TB;
                else type[v] = -1;
            }
            int cross = 0;
            for (int e = 0; e < ne; e++) if (sub(&em[e], &J) && !sub(&em[e], &KA) && !sub(&em[e], &KB)) cross++;
            /* typed post-join propagation; covered set tracked by 'done' flags */
            int done[MAXE]; for (int e = 0; e < ne; e++) done[e] = sub(&em[e], &J);
            int sep = 0, nonsep = 0, acc = 0;
            for (;;) {
                int beste = -1, bestt = 99, bestw = -1;
                for (int e = 0; e < ne; e++) { if (done[e]) continue;
                    int unk = -1, nu = 0, ts[4], nt = 0;
                    for (int i = 0; i < nev[e]; i++) { int v = ev[e][i]; if (!has(&J, v)) { unk = v; nu++; } else ts[nt++] = type[v]; }
                    if (nu != 1) continue;
                    int t = restype(e, ts, nt); if (t < bestt || (t == TSP || t == TSX) && bestt == TM) { bestt = t; beste = e; bestw = unk; }
                }
                if (beste < 0) {
                    if (!LOOK || pc(&J) == nv) break;
                    int z = lookone(&J); if (z < 0) break;
                    setb(&J, z); type[z] = TM; acc++;
                } else { setb(&J, bestw); type[bestw] = bestt; done[beste] = 1; }
                for (int e = 0; e < ne; e++) { if (done[e] || !sub(&em[e], &J)) continue;
                    done[e] = 1; int ts[4]; for (int i = 0; i < nev[e]; i++) ts[i] = type[ev[e][i]];
                    int t = restype(e, ts, nev[e]); if (t == TM) nonsep++; else sep++; }
            }
            if (pc(&J) != nv) continue;
            int pf = nonsep - acc; if (pf < 0) pf = 0;
            /* independent join conditions at the join by excess counting (shared words alone overcount) */
            int Ej = ncov(&J0) - ncov(&Kc), Dj = pc(&J0) - pc(&Kc) - na - nb;
            int jjoin = Ej - Dj - iA - iB; if (jjoin < 0) jjoin = 0;
            int jc = jjoin + sep;
            if (jc > maxjc) maxjc = jc;
            double cst = bestcost(na, nb, nc, iA, iB, jc, pf);
            if (cst < best || (cst == best && jc > bestjc)) {
                best = cst; bestjc = jc;
                int o = sprintf(desc, "core{"); for (int i = 0; i < g; i++) if (role[i] == 0) o += sprintf(desc + o, " %s", names[G[i]]);
                o += sprintf(desc + o, " } A{"); for (int i = 0; i < g; i++) if (role[i] == 1) o += sprintf(desc + o, " %s", names[G[i]]);
                o += sprintf(desc + o, " } B{"); for (int i = 0; i < g; i++) if (role[i] == 2) o += sprintf(desc + o, " %s", names[G[i]]);
                sprintf(desc + o, " } jcJoin=%d (shared=%d cross=%d) sepPost=%d iA=%d iB=%d postFilters=%d postAcc=%d", jjoin, shared, cross, sep, iA, iB, pf, acc);
            }
        }
        if (best < overall) overall = best;
        hist[(int)best < 200 ? (int)best : 199]++;
        if (maxjc > gmaxjc) gmaxjc = maxjc;
        printf("set%d g=%d best cost exponent %.0f ; max join conditions over all splits %d : %s\n", nsets, g, best, maxjc, desc); fflush(stdout);
    }
    printf("SUMMARY sets=%d best cost exponent over all sets = %.0f ; max join conditions in any split of any set = %d ; histogram:", nsets, overall, gmaxjc);
    for (int i = 0; i < 200; i++) if (hist[i]) printf(" %d:%d", i, hist[i]);
    printf("\n");
    return 0;
}
