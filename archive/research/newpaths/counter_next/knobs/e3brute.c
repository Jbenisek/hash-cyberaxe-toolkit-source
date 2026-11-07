/* e3brute.c (counter_next/knobs; research only): brute force over ALL 2^32 values of h1 for one outer step
 * U = (y, Y9, w8), against targets given as hex pairs DG1:DE2 (partial system) or quads DG1:DE2:DG2:DF2 (full).
 * Prints every solution "h1 targetindex" in increasing h1, then the count.  Compared with e3dfs.py output.
 * usage: e3brute Y Y9 W8 TARGETFILE      (hex; TARGETFILE: targets separated by blanks)
 */
#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
typedef uint32_t u32;
static inline u32 ror(u32 x, int r) { return (x >> r) | (x << (32 - r)); }
#define Y3 0x8127c181u
#define Y3B 0x7edf3e7eu
#define ETA 0x830303cfu
#define NT 512
static u32 tg1[NT], te2[NT], tg2[NT], tf2[NT];
static int full[NT], nxt[NT], head[65536];
int main(int argc, char **argv) {
    if (argc < 5) { fprintf(stderr, "usage\n"); return 1; }
    u32 y = strtoul(argv[1], 0, 16), Y9 = strtoul(argv[2], 0, 16), w8 = strtoul(argv[3], 0, 16);
    FILE *f = fopen(argv[4], "r");
    char buf[128]; int nt = 0;
    for (int i = 0; i < 65536; i++) head[i] = -1;
    while (nt < NT && fscanf(f, "%127s", buf) == 1) {
        char *s = buf;
        tg1[nt] = strtoul(s, &s, 16); s++; te2[nt] = strtoul(s, &s, 16); full[nt] = 0;
        if (*s == ':') { s++; tg2[nt] = strtoul(s, &s, 16); s++; tf2[nt] = strtoul(s, &s, 16); full[nt] = 1; }
        nxt[nt] = head[tg1[nt] & 0xffff]; head[tg1[nt] & 0xffff] = nt; nt++;
    }
    fclose(f);
    u32 e1 = Y3 + y, e1b = Y3B + y;
    unsigned long long n = 0;
    for (unsigned long long hh = 0; hh < (1ull << 32); hh++) {
        u32 h = (u32)hh, hb = h ^ ETA;
        u32 g1 = Y9 + h, g1b = Y9 + hb, dg1 = g1 ^ g1b;
        int i = head[dg1 & 0xffff];
        if (i < 0) continue;
        u32 f1 = ror(y ^ g1, 12), f1b = ror(y ^ g1b, 12);
        u32 e2 = e1 + f1 + w8, e2b = e1b + f1b + w8, de2 = e2 ^ e2b;
        u32 h2 = ror(h ^ e2, 8), h2b = ror(hb ^ e2b, 8);
        u32 g2 = g1 + h2, g2b = g1b + h2b, dg2 = g2 ^ g2b;
        u32 df2 = ror(f1 ^ g2, 7) ^ ror(f1b ^ g2b, 7);
        /* report in target-file order for each h (sorted later) */
        for (; i >= 0; i = nxt[i]) {
            if (dg1 != tg1[i] || de2 != te2[i]) continue;
            if (full[i] && (dg2 != tg2[i] || df2 != tf2[i])) continue;
            printf("%08x %d\n", h, i); n++;
        }
    }
    printf("# count %llu\n", n);
    return 0;
}
