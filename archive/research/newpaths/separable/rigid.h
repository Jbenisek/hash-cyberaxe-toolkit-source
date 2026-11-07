/* rigid.h - closure with an extra rule (model "rigid"): small square subsystems solved by a table.
 * After plain propagation + macros, any 2 equations whose unknown words are the same 2 words, or any 3
 * equations whose unknown words lie in a common set of 3 words (each pair covering >= 2 of them, so a
 * perfect matching exists), are solved when the known words of those equations number <= 2
 * (table indexed by <= 2 words: 2^64 entries, preprocessing <= 2^64).  All words in the system files are
 * non-constant, so "known words of the equations" = table parameters.
 * Include after jtree_core.h.
 */
static long rigid_fires;
static M closure_rigid(M K) {
    for (;;) {
        K = closure(K);
        if (K == ALL) return K;
        int act[MAXE], na = 0;
        M un[MAXE];
        for (int e = 0; e < E; e++) {
            M u = emask[e] & ~K; int p = pc(u);
            if (p == 2 || p == 3) { un[na] = u; act[na++] = e; }
        }
        int fired = 0;
        for (int i = 0; i < na && !fired; i++) {
            for (int j = i + 1; j < na && !fired; j++) {
                M U = un[i] | un[j];
                int pu = pc(U);
                if (pu == 2) {
                    M par = (emask[act[i]] | emask[act[j]]) & K;
                    if (pc(par) <= 2) { K |= U; fired = 1; rigid_fires++; }
                } else if (pu == 3) {
                    for (int l = j + 1; l < na && !fired; l++) {
                        if (un[l] & ~U) continue;
                        if (pc(un[i] | un[l]) < 2 || pc(un[j] | un[l]) < 2) continue;
                        M par = (emask[act[i]] | emask[act[j]] | emask[act[l]]) & K;
                        if (pc(par) <= 2) { K |= U; fired = 1; rigid_fires++; }
                    }
                }
            }
        }
        if (!fired) return K;
    }
}
