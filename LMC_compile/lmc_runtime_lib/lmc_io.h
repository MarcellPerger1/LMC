#ifndef _LMC_IO_H
#define _LMC_IO_H

#include <stdio.h>
#include <wchar.h>
#include <inttypes.h>

#include "concise_inttypes.h"
#include "lmc_assert.h"

// WARNING: This uses wprintf so everything in the rest 
// of the program must also use wprintf to avoid UB


typedef struct _LmcIoS {
    bool is_line_mode;
    bool addPromptS;
} LmcIoT;

LmcIoT LmcIo_create1(bool addPromptS) {
    LmcIoT lio = {
        false,
        addPromptS
    };
    return lio;
}

LmcIoT LmcIo_create0() {
    return LmcIo_create1(true);
}

void LmcIo_writeChar(LmcIoT* self, i32 value) {
    u32 uval = (u32)value;
    wchar_t wch = (wchar_t)uval;
    wprintf(L"%c", wch);
    if(wch == L'\n') {
        self->is_line_mode = false;  // end of line; reset to normal
    } else {
        self->is_line_mode = true;  // middle of line - keep outputting on this line
    }
}

void LmcIo_writeNum(LmcIoT* self, i32 value) {
    if(self->is_line_mode) {
        wprintf(L"%" PRIi32, value);
    } else {
        wprintf(L"%" PRIi32 L"\n", value);
    }
}

i32 LmcIo_readNum(LmcIoT* self) {
    i32 ival;
    wchar_t endch;
    // I really hope this works - IO + strings in C is a MESS
    for(;;) {
        if(self->addPromptS) { wprintf(L">? \n"); }
        int nargs = wscanf(L" %" SCNi32  L"%*2000[ \t]%c", &ival, &endch);
        LmcAssert_FATAL2(nargs != EOF, "End of stdin reached, aborting");
        if(nargs == 0) {
            wprintf(L"Input must be string");
            continue;
        }
        if(nargs == 1) {  // next char is newline
            return ival;
        }
        LmcAssert_FATAL2(nargs == 2, "Only 2 extra args provided to wscanf, only 2 should be assigned");
        if(endch == L'\n') {
            return ival;
        }
        wprintf(L"Input too big");
    }
}

#endif
