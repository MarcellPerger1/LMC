#ifndef _LMC_MEM_H
#define _LMC_MEM_H

#include <limits.h>
#if UCHAR_MAX != 0xFF
#error unsinged char must be 1 byte
#endif

#include <stdlib.h>
#include <string.h>

#include "concise_inttypes.h"
#include "lmc_assert.h"

typedef struct _LmcMemoryS {
    usize len;
    i32* mem_ptr;
} LmcMemT;

void LmcMem_copyFrom(LmcMemT* self, const i32* src_buf, usize src_sz);

// Ownership of `buf` transferred to the `LmcMemT`
LmcMemT LmcMem_fromBuf(i32* buf, usize len) {
    LmcMemT self = {len, buf};
    return self;
}
LmcMemT LmcMem_createZeroed(usize len) {
    i32* mem_ptr = (i32*)calloc(len, sizeof(i32));
    return LmcMem_fromBuf(mem_ptr, len);
}
LmcMemT LmcMem_createCopyBuf(i32* srcbuf, usize srclen) {
    // TODO security: check for overflow or whatever
    i32* buf = (i32*)malloc(srclen * sizeof(i32));
    LmcMemT self = LmcMem_fromBuf(buf, srclen);
    LmcMem_copyFrom(&self, srcbuf, srclen);
    return self;
}
LmcMemT LmcMem_createCopyResize(i32* srcbuf, usize srclen, usize newlen) {
    if(srclen == newlen) return LmcMem_createCopyBuf(srcbuf, newlen);
    // Only copy newlen of srcbuf
    if(srclen > newlen) return LmcMem_createCopyBuf(srcbuf, newlen);
    LmcAssert_FATALX(newlen > srclen);
    // Here, we need to copy into the first half, then memset(0) the 2nd half
    i32* newbuf = (i32*)malloc(newlen * sizeof(i32));
    memcpy(newbuf, srcbuf, srclen * sizeof(i32));
    // 0 1 ... srclen-1 | srclen srlen+1 ... newlen-1
    // <----------------+-newlen-------------------->
    // <----srclen----> | <----(newlen - srclen)---->
    i32* newbuf_zeroes_start = &newbuf[srclen];
    usize nzeroes = newlen - srclen;
    memset(newbuf_zeroes_start, 0, nzeroes * sizeof(i32));
    return LmcMem_fromBuf(newbuf, newlen);
}


// `src_sz`: Amount of `i32`s to copy
void LmcMem_copyFrom(LmcMemT* self, const i32* src_buf, usize src_sz) {
    LmcAssert_FATALX(self->len >= src_sz, "Not enough space in self to do LmcMem_copyFrom()");
    // TODO security: check for overflow or whatever
    usize nbytes = src_sz * sizeof(i32);
    memcpy(self->mem_ptr, src_buf, nbytes);
}

inline i32 LmcMem_get(const LmcMemT* self, usize i) {
    LmcAssert_FATAL2(i < self->len, "Cannot get memory; index out of range");
    return self->mem_ptr[i];
}
inline void LmcMem_set(LmcMemT* self, usize i, i32 v) {
    LmcAssert_FATAL2(i < self->len, "Cannot set memory; index out of range");
    self->mem_ptr[i] = v;
}

#endif