#ifndef _LMC_MEM_H
#define _LMC_MEM_H

#include "concise_inttypes.h"
#include "lmc_assert.h"

typedef struct _LmcMemoryS {
    usize len;
    i32* mem_ptr;
} LmcMemT;

inline u32 LmcMem_get(const LmcMemT* mem, usize i) {
    LmcAssert_FATAL2(i < mem->len, "Memory index out of range");
    return mem->mem_ptr[i];
}

inline void LmcMem_set(LmcMemT* mem, usize i, i32 v) {
    LmcAssert_FATAL2(i < mem->len, "Memory index out of range");
    mem->mem_ptr[i] = v;
}

#endif