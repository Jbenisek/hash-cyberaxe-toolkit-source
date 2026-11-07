#ifndef OUTBUF_H
#define OUTBUF_H
#include <stddef.h>
#define OUTCAP 8192              /* capacity of the output buffer: the whole report is appended to it and written by one write */
void out_flush(void);
extern size_t out_len;
#endif
