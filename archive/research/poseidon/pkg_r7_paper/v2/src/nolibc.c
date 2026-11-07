/* Minimal runtime for the statically linked, libc-free executable (no C library is linked): the process entry, the Linux system calls the program uses
 * (write once, exit_group once), memcpy / memset / memmove / strcmp, and a small printf that appends the report to one output buffer.  The printf has no
 * integer division, no modulo and no floating point: a decimal number is formed by comparing with the powers of ten and subtracting them, a hexadecimal one by
 * shifts and masks.
 * There is no mmap, munmap or clock system call: memory is one static arena (common.c) and the program reads no clock.
 * What executes here is charged in single.c, stage I (process entry, the formatting of the whole output buffer, the single write, exit_group). */
#include <stdint.h>
#include <stddef.h>
#include <stdarg.h>
#include <stdio.h>
#include "outbuf.h"

static inline long sys3(long n, long a, long b, long c) { long r; __asm__ volatile("syscall" : "=a"(r) : "0"(n), "D"(a), "S"(b), "d"(c) : "rcx", "r11", "memory"); return r; }
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

/* printf: %d %i %u %x %s %c %% with flags '-' and '0', width, precision for %s, length l ll z (no %f) */
static const uint64_t P10[20] = { 1ULL, 10ULL, 100ULL, 1000ULL, 10000ULL, 100000ULL, 1000000ULL, 10000000ULL, 100000000ULL, 1000000000ULL, 10000000000ULL, 100000000000ULL,
    1000000000000ULL, 10000000000000ULL, 100000000000000ULL, 1000000000000000ULL, 10000000000000000ULL, 100000000000000000ULL, 1000000000000000000ULL, 10000000000000000000ULL };
static int vfmt(char *o, size_t cap, const char *f, va_list ap) {
    size_t n = 0;
#define PUT(ch) do { if (n < cap) o[n] = (ch); n++; } while (0)
    for (; *f; f++) {
        if (*f != '%') { PUT(*f); continue; }
        f++;
        int left = 0, zero = 0, w = 0, prec = -1, lng = 0;
        for (;; f++) { if (*f == '-') left = 1; else if (*f == '0') zero = 1; else break; }
        while (*f >= '0' && *f <= '9') w = (w << 3) + (w << 1) + (*f++ - '0');
        if (*f == '.') { f++; prec = 0; while (*f >= '0' && *f <= '9') prec = (prec << 3) + (prec << 1) + (*f++ - '0'); }
        while (*f == 'l' || *f == 'z') { lng = 1; f++; }
        char tmp[80]; int tl = 0; const char *src = tmp; char c = *f;
        if (c == '%') { PUT('%'); continue; }
        if (c == 'c') { tmp[tl++] = (char)va_arg(ap, int); }
        else if (c == 's') { src = va_arg(ap, const char *); if (!src) src = "(null)"; while (src[tl] && (prec < 0 || tl < prec)) tl++; }
        else if (c == 'd' || c == 'i' || c == 'u' || c == 'x') {
            uint64_t v; int neg = 0;
            if (c == 'd' || c == 'i') { int64_t sv = lng ? va_arg(ap, long) : va_arg(ap, int); if (sv < 0) { neg = 1; v = (uint64_t)0 - (uint64_t)sv; } else v = (uint64_t)sv; }
            else v = lng ? va_arg(ap, unsigned long) : va_arg(ap, unsigned);
            if (neg) tmp[tl++] = '-';
            if (c == 'x') { int k = 15; while (k > 0 && !((v >> (k << 2)) & 15)) k--; for (; k >= 0; k--) tmp[tl++] = "0123456789abcdef"[(v >> (k << 2)) & 15]; }
            else { int k = 19; while (k > 0 && v < P10[k]) k--; for (; k >= 0; k--) { char dg = 0; while (v >= P10[k]) { v -= P10[k]; dg++; } tmp[tl++] = (char)('0' + dg); } }
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
/* The report is appended to one static buffer of OUTCAP bytes; nothing is written until out_flush, which makes the single write system call. */
static char outbuf[OUTCAP]; size_t out_len = 0;
static void out_put(int fd, const char *p, size_t n) {
    if (fd != 1) { wr(fd, p, n); return; }                /* stderr: error paths only, never executed in the recorded run */
    for (size_t k = 0; k < n; k++) { if (out_len < OUTCAP) outbuf[out_len] = p[k]; out_len++; }
}
static int vout(int fd, const char *f, va_list ap) {
    if (fd != 1) { char b[1024]; int n = vfmt(b, sizeof b, f, ap); if (n > (int)sizeof b) n = (int)sizeof b; wr(fd, b, (size_t)n); return n; }
    int n = vfmt(outbuf + (out_len < OUTCAP ? out_len : OUTCAP), out_len < OUTCAP ? OUTCAP - out_len : 0, f, ap); out_len += (size_t)n; return n;
}
void out_flush(void) { wr(1, outbuf, out_len < OUTCAP ? out_len : OUTCAP); }
FILE *stdout = (FILE *)1, *stderr = (FILE *)2;
int printf(const char *f, ...) { va_list ap; va_start(ap, f); int n = vout(1, f, ap); va_end(ap); return n; }
int fprintf(FILE *fp, const char *f, ...) { va_list ap; va_start(ap, f); int n = vout((int)(intptr_t)fp, f, ap); va_end(ap); return n; }
int puts(const char *s) { out_put(1, s, strlen(s)); out_put(1, "\n", 1); return 0; }
int putchar(int c) { char ch = (char)c; out_put(1, &ch, 1); return c; }
int fputc(int c, FILE *fp) { char ch = (char)c; out_put((int)(intptr_t)fp, &ch, 1); return c; }
int putc(int c, FILE *fp) { return fputc(c, fp); }
int fputs(const char *s, FILE *fp) { out_put((int)(intptr_t)fp, s, strlen(s)); return 0; }
size_t fwrite(const void *p, size_t sz, size_t n, FILE *fp) { for (size_t i = 0; i < n; i++, p = (const char *)p + sz) out_put((int)(intptr_t)fp, (const char *)p, sz); return n; }   /* gcc turns fprintf(stderr, "text") into fwrite; error paths only; no multiplication */
int fflush(FILE *fp) { (void)fp; return 0; }

int main(int, char **);
void par_tls_boot(void);
void c_start(long *sp) { par_tls_boot(); int argc = (int)sp[0]; exit(main(argc, (char **)(sp + 1))); }
__asm__(".globl _start\n_start:\n xor %ebp,%ebp\n mov %rsp,%rdi\n and $-16,%rsp\n call c_start\n");
