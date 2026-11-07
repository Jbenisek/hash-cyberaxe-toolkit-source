/* Native x86-64 wrapper of gen.c for the memory check (not shipped): a static freestanding binary without libc that runs the generator and writes
   the result record and the instruction records to fd 1.  Run under `prlimit --as=1048576` (address space capped at 1 MiB, code, data, bss and stack). */
#include "../gen.c"
static long sys3(long n, long a, long b, long c) { long r; __asm__ volatile("syscall" : "=a"(r) : "a"(n), "D"(a), "S"(b), "d"(c) : "rcx", "r11", "memory"); return r; }
void *memset(void *d, int c, unsigned long n) { unsigned char *p = d; while (n--) *p++ = (unsigned char)c; return d; }
void *memcpy(void *d, const void *s, unsigned long n) { unsigned char *p = d; const unsigned char *q = s; while (n--) *p++ = *q++; return d; }
void _start(void) {
  int rc = run();
  sys3(1, 1, (long)&info, (long)sizeof info);
  unsigned long len = (unsigned long)cb, off = 0;
  while (off < len) { long w = sys3(1, 1, (long)(code + off), (long)(len - off)); if (w <= 0) break; off += (unsigned long)w; }
  sys3(231, rc, 0, 0);
}
