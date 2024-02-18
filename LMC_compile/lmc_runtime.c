#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <stdbool.h>

#include "lmc_runtime_lib/lmc_interp.h"

typedef struct {
    i32 a;
    i32 b;
} intpair;


int main(int argc, char** argv) {
    (void)argc;(void)argv;

    #define PSZ 4

    intpair PRGPAIR[PSZ] = {
        {9, 1},  // INP
        {1, 3},  // ADD one
        {9, 2},  // OUT
        {0, 1},  // one DAT 1
    };
    i32 PRG[PSZ];
    for(usize i=0; i<PSZ; ++i) {
        intpair pair = PRGPAIR[i];
        i32 res;
        if(pair.a == 0) {
            res = pair.b;
        } else {
            res = pair.a << 27 | pair.b & 0x07'FF'FF'FF;
        }
        PRG[i] = res;
    }
    LmcInterpT lmc = LmcInterp_create_fromBuf(PRG, PSZ, true);
    LmcInterp_main(&lmc);
    // wprintf(L"Hello world, %zi\n", sizeof(LmcMemT));
    return 0;
}
