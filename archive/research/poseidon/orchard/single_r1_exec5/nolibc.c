/* Minimal runtime for the statically linked, libc-free executable (no C library is linked): the process entry, the Linux system calls the program uses
 * (write, mmap, munmap, clock_gettime, exit_group), memcpy / memset / memmove / strcmp, a small printf for the report lines, log2 and clock.
 * Nothing here is charged: it is the machinery of the executable, not part of the counted algorithm. */
#include <stdint.h>
#include <stddef.h>
#include <stdarg.h>
#include <stdio.h>
#include <time.h>

static inline long sys3(long n, long a, long b, long c) { long r; __asm__ volatile("syscall" : "=a"(r) : "0"(n), "D"(a), "S"(b), "d"(c) : "rcx", "r11", "memory"); return r; }
static inline long sys6(long n, long a, long b, long c, long d, long e, long f) {
    long r; register long r10 __asm__("r10") = d; register long r8 __asm__("r8") = e; register long r9 __asm__("r9") = f;
    __asm__ volatile("syscall" : "=a"(r) : "0"(n), "D"(a), "S"(b), "d"(c), "r"(r10), "r"(r8), "r"(r9) : "rcx", "r11", "memory"); return r;
}
void *sys_map(size_t bytes) { long r = sys6(9, 0, (long)bytes, 3, 0x22, -1, 0); return (r < 0 && r > -4096) ? NULL : (void *)r; }   /* PROT_READ|PROT_WRITE, MAP_PRIVATE|MAP_ANONYMOUS */
void sys_unmap(void *p, size_t bytes) { sys3(11, (long)p, (long)bytes, 0); }
void exit(int code) { for (;;) sys3(231, code, 0, 0); }
static void wr(int fd, const char *s, size_t n) { while (n) { long r = sys3(1, fd, (long)s, (long)n); if (r <= 0) return; s += r; n -= (size_t)r; } }

void *memcpy(void *d, const void *s, size_t n) { void *r = d; __asm__ volatile("rep movsb" : "+D"(d), "+S"(s), "+c"(n) : : "memory"); return r; }
void *memset(void *d, int c, size_t n) { void *r = d; __asm__ volatile("rep stosb" : "+D"(d), "+c"(n) : "a"(c) : "memory"); return r; }
void *memmove(void *d, const void *s, size_t n) {
    if ((uintptr_t)d <= (uintptr_t)s || (uintptr_t)d >= (uintptr_t)s + n) return memcpy(d, s, n);
    unsigned char *dd = d; const unsigned char *ss = s; while (n--) dd[n] = ss[n]; return d;
}
int strcmp(const char *a, const char *b) { while (*a && *a == *b) { a++; b++; } return (unsigned char)*a - (unsigned char)*b; }
size_t strlen(const char *s) { size_t n = 0; while (s[n]) n++; return n; }

clock_t clock(void) { struct { long s, ns; } ts; sys3(228, 2, (long)&ts, 0); return (clock_t)(ts.s * 1000000L + ts.ns / 1000); }   /* CLOCK_PROCESS_CPUTIME_ID, microseconds */
double log2(double x) {
    union { double d; uint64_t u; } v = { x };
    int e = (int)((v.u >> 52) & 0x7ff) - 1023; v.u = (v.u & 0x000fffffffffffffULL) | 0x3ff0000000000000ULL;
    double z = (v.d - 1) / (v.d + 1), z2 = z * z, t = z, s = 0;
    for (int k = 1; k < 60; k += 2) { s += t / k; t *= z2; }
    return e + 2 * s / 0.69314718055994530942;
}

/* printf: %d %i %u %x %s %c %% with flags '-' and '0', width, precision for %f/%s, length l ll z; %f for non-negative values below 1e15 */
static int vfmt(char *o, size_t cap, const char *f, va_list ap) {
    size_t n = 0;
#define PUT(ch) do { if (n < cap) o[n] = (ch); n++; } while (0)
    for (; *f; f++) {
        if (*f != '%') { PUT(*f); continue; }
        f++;
        int left = 0, zero = 0, w = 0, prec = -1, lng = 0;
        for (;; f++) { if (*f == '-') left = 1; else if (*f == '0') zero = 1; else break; }
        while (*f >= '0' && *f <= '9') w = w * 10 + (*f++ - '0');
        if (*f == '.') { f++; prec = 0; while (*f >= '0' && *f <= '9') prec = prec * 10 + (*f++ - '0'); }
        while (*f == 'l' || *f == 'z') { lng = 1; f++; }
        char tmp[80]; int tl = 0; const char *src = tmp; char c = *f;
        if (c == '%') { PUT('%'); continue; }
        if (c == 'c') { tmp[tl++] = (char)va_arg(ap, int); }
        else if (c == 's') { src = va_arg(ap, const char *); if (!src) src = "(null)"; while (src[tl] && (prec < 0 || tl < prec)) tl++; }
        else if (c == 'd' || c == 'i' || c == 'u' || c == 'x') {
            uint64_t v; int neg = 0;
            if (c == 'd' || c == 'i') { int64_t sv = lng ? va_arg(ap, long) : va_arg(ap, int); if (sv < 0) { neg = 1; v = (uint64_t)0 - (uint64_t)sv; } else v = (uint64_t)sv; }
            else v = lng ? va_arg(ap, unsigned long) : va_arg(ap, unsigned);
            unsigned b = c == 'x' ? 16 : 10; char r[24]; int rl = 0;
            do { r[rl++] = "0123456789abcdef"[v % b]; v /= b; } while (v);
            if (neg) tmp[tl++] = '-';
            while (rl) tmp[tl++] = r[--rl];
        } else if (c == 'f') {
            double v = va_arg(ap, double); int p = prec < 0 ? 6 : prec;
            if (v < 0) { tmp[tl++] = '-'; v = -v; }
            uint64_t sc = 1; for (int i = 0; i < p; i++) sc *= 10;
            uint64_t q = (uint64_t)(v * (double)sc + 0.5), ip = q / sc, fp = q % sc; char r[24]; int rl = 0;
            do { r[rl++] = (char)('0' + ip % 10); ip /= 10; } while (ip);
            while (rl) tmp[tl++] = r[--rl];
            if (p) { tmp[tl++] = '.'; for (int i = p - 1; i >= 0; i--) { uint64_t d = fp; for (int j = 0; j < i; j++) d /= 10; tmp[tl++] = (char)('0' + d % 10); } }
        } else { PUT('%'); PUT(c); continue; }
        int pad = w > tl ? w - tl : 0;
        if (!left) { char pc = (zero && c != 's') ? '0' : ' '; if (pc == '0' && tl && src[0] == '-') { PUT('-'); src++; tl--; } for (int i = 0; i < pad; i++) PUT(pc); }
        for (int i = 0; i < tl; i++) PUT(src[i]);
        if (left) for (int i = 0; i < pad; i++) PUT(' ');
    }
    return (int)n;
}
int vsnprintf(char *o, size_t cap, const char *f, va_list ap) { int n = vfmt(o, cap ? cap - 1 : 0, f, ap); if (cap) o[(size_t)n < cap - 1 ? (size_t)n : cap - 1] = 0; return n; }
int snprintf(char *o, size_t cap, const char *f, ...) { va_list ap; va_start(ap, f); int n = vsnprintf(o, cap, f, ap); va_end(ap); return n; }
static int vout(int fd, const char *f, va_list ap) { char b[1024]; int n = vfmt(b, sizeof b, f, ap); if (n > (int)sizeof b) n = (int)sizeof b; wr(fd, b, (size_t)n); return n; }
FILE *stdout = (FILE *)1, *stderr = (FILE *)2;
int printf(const char *f, ...) { va_list ap; va_start(ap, f); int n = vout(1, f, ap); va_end(ap); return n; }
int fprintf(FILE *fp, const char *f, ...) { va_list ap; va_start(ap, f); int n = vout((int)(intptr_t)fp, f, ap); va_end(ap); return n; }
int puts(const char *s) { wr(1, s, strlen(s)); wr(1, "\n", 1); return 0; }
int putchar(int c) { char ch = (char)c; wr(1, &ch, 1); return c; }
int putc(int c, FILE *fp) { char ch = (char)c; wr((int)(intptr_t)fp, &ch, 1); return c; }
int fputs(const char *s, FILE *fp) { wr((int)(intptr_t)fp, s, strlen(s)); return 0; }
size_t fwrite(const void *p, size_t sz, size_t n, FILE *fp) { wr((int)(intptr_t)fp, p, sz * n); return n; }
int fflush(FILE *fp) { (void)fp; return 0; }

int main(int, char **);
void c_start(long *sp) { int argc = (int)sp[0]; exit(main(argc, (char **)(sp + 1))); }
__asm__(".globl _start\n_start:\n xor %ebp,%ebp\n mov %rsp,%rdi\n and $-16,%rsp\n call c_start\n");
