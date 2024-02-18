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

LmcIoT LmcIo_create0(void) {
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

void _LmcIo_wstdinConsumeSpaces() {
    // There is a reason for size=8: this will be 8*16=128 bits (wchar_t = 16 bits on MSVC) 
    //   or 8*32=256 bits (wchar_t = 8 bits on gcc) so this will fits exactly into an XMM/YMM register
    wchar_t dummy_buf[8];  // so that we can use the return value of wscanf
    for(;;) {
        switch(wscanf(L"%7l[ \t\f]", dummy_buf)) {
            case EOF: {
                LmcAssert_UNREACHABLE1("End of stding reached, aborting");
            } case 0: {
                // Consumed <7 chars of whitespace so must be end of whitespace
                return;
            } case 1: {
                // Filled up all 7 chars so continue
                continue;
            } default: {
                LmcAssert_UNREACHABLE0();
            }
        }
    }
}
void _LmcIo_wstdinConsumeLine() {
    wchar_t dummy_buf[8];  // so that we can use the return value of wscanf
    for(;;) {
        switch (wscanf(L"%7l[^\n]", dummy_buf)) {
            case EOF: {
                LmcAssert_UNREACHABLE1("End of string reached, aborting");
            } case 0: {
                return;  // filled <7 chars; return
            } case 1: {
                continue;  // filled up all 7 chars
            } default: {
                LmcAssert_UNREACHABLE0();
            }
        }
    }
}

i32 LmcIo_readNum(LmcIoT* self) {
    i32 ival;
    // I really hope this works - IO + strings in C is a MESS
    for(;;) {
        if(self->addPromptS) { wprintf(L">? "); }
        _LmcIo_wstdinConsumeSpaces();
        int nargs_i = wscanf(L"%" SCNi32, &ival);
        LmcAssert_FATAL2(nargs_i != EOF, "End of stding reached, aborting");
        if(nargs_i == 0) {
            _LmcIo_wstdinConsumeLine();
            wprintf(L"Input must be an integer\n");
            continue;
        }
        _LmcIo_wstdinConsumeSpaces();
        wint_t next_char = getwchar();
        LmcAssert_FATAL2(next_char != WEOF, "End of stdin reached, aborting");
        if((wchar_t)next_char == L'\n') {
            // End of line after the number so allow
            return ival;
        }
        // More non-space chars that are not part of the number so just consume rest of line
        _LmcIo_wstdinConsumeLine();
        wprintf(L"Input must be an integer32\n");
    }
}

#endif
