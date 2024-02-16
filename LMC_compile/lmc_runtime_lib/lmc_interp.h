#ifndef _LMC_INTERP_H
#define _LMC_INTERP_H

#include <stdbool.h>

#include "lmc_mem.h"
#include "lmc_io.h"

// surprisingly this struct itself is only 32B, including padding
// see https://godbolt.org/z/qPf5hPevK
typedef struct _LmcInterpS {
    LmcMemT mem;
    usize ip;
    u32 acc;
    LmcIoT io;
    bool is_halted;
} LmcInterpT;

LmcInterpT LmcInterp_createFromMem(LmcMemT mem, bool add_prompt) {
    LmcInterpT self = {
        .mem = mem,
        .io = LmcIo_create1(add_prompt),
        .acc = 0,
        .ip = 0,
        .is_halted = false,
    };
    return self;
}
// `mem_len`: Amount of i32 in the `mem_buf`
// `mem_buf`: Ownership is de facto transferred to the LmcInterpT
LmcInterpT LmcInterp_create_fromBuf(i32* mem_buf, usize mem_len, bool add_prompt) {
    return LmcInterp_createFromMem(LmcMem_fromBuf(mem_buf, mem_len), add_prompt);
}
// `mem_len`: Amount of i32 we can store
LmcInterpT LmcInterp_createEmpty(usize mem_len, bool add_prompt) {
    return LmcInterp_createFromMem(LmcMem_createZeroed(mem_len), add_prompt);
}
// `mem_len`: Amount of i32 in the `mem_buf`
LmcInterpT LmcInterp_create_copyBuf(i32* mem_buf, usize mem_len, bool add_prompt) {
    return LmcInterp_createFromMem(LmcMem_createCopyBuf(mem_buf, mem_len), add_prompt);
}
LmcInterpT LmcInterp_createCopyResize(i32* srcbuf, usize srclen, usize newlen, bool add_prompt) {
    return LmcInterp_createFromMem(LmcMem_createCopyResize(srcbuf, srclen, newlen), add_prompt);
}

u32 LmcInterp_fetchCurrInstr(const LmcInterpT* self) {
    i32 sinstr = LmcMem_get(&self->mem, self->ip);
    return (u32)sinstr;
}

// abort()s on invalid operand
void LmcInterp_handleIoInstr(LmcInterpT* self, u32 operand32) {
    switch(operand32) {
        case 1: {  // INP
            self->acc = LmcIo_readNum(&self->io); break;
        } case 2: {
            LmcIo_writeNum(&self->io, self->acc); break;
        } case 22: {
            LmcIo_writeChar(&self->io, self->acc); break;
        } default: {
            LmcAssert_FATALX("Invalid operand of IO instruction");
        }
    }
}

// abort()s on invalid instruction or OOB read/write
void LmcInterp_main(LmcInterpT* self) {
    LmcMemT* mem = &self->mem;
    while(!self->is_halted) {
        // FETCH
        u32 cir = LmcInterp_fetchCurrInstr(self);
        // DECODE
        // 5 MSB; the `& 0x1F` is just to make it explicit to the compiler that its 5 bits
        u32 opcode = (cir >> 27) & 0x1F;
        u32 operand32 = cir & 0x07'FF'FF'FF;  // 27 LSB
        usize operand = (usize)operand32;
        // EXECUTE
        switch(opcode) {
            case 0: {  // HLT
                self->is_halted = true; break;
            } case 1: {  // ADD
                self->acc += LmcMem_get(mem, operand); break;
            } case 2: {  // SUB
                self->acc -= LmcMem_get(mem, operand); break;
            } case 3: {  // STA
                LmcMem_set(mem, operand, self->acc); break;
            } case 4: {
                LmcAssert_FATALX(false, "Opcode 4 is invalid");
            } case 5: {  // LDA
                self->acc = LmcMem_get(mem, operand); break;
            } case 6: {  // BRA
                self->ip = operand; break;
            } case 7: {  // BRZ
                if(self->acc == 0) self->ip = operand; break;
            } case 8: {  // BRP
                if(self->acc >= 0) self->ip = operand; break;
            } case 9: {  // IO
                LmcInterp_handleIoInstr(self, operand32); break;
            } default: {
                LmcAssert_FATALX(false, "Invalid opcode encountered");
            }
        }
    }
}

#endif