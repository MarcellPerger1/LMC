#ifndef _LMC_ASSERT_H
#define _LMC_ASSERT_H

#include <stdio.h>
#include <stdlib.h>
#include <stdbool.h>
#include <stdnoreturn.h>

#define _LmcAssert_INTERN_GETARG3(a1,a2,a3,...) a3
// Error messages gonna be real bad this one
#define LmcAssert_FATALX(...) _LmcAssert_INTERN_GETARG3(__VA_ARGS__, _LmcAssert_AssertMsgFatal_Func, _LmcAssert_AssertFatal_Func)\
    (__VA_ARGS__, __FILE__, __LINE__, __FUNCTION__)
#define LmcAssert_FATAL1(cond) _LmcAssert_AssertFatal_Func(cond, __FILE__, __LINE__, __FUNCTION__)
#define LmcAssert_FATAL2(cond, msg) _LmcAssert_AssertMsgFatal_Func(cond, msg, __FILE__, __LINE__, __FUNCTION__)


noreturn void _LmcAssert_FailWithMsg(const char* msg, const char* dunder_file, int dunder_line, const char* dunder_func) {
    fprintf(stderr, "%s:%i %s (in function %s)", dunder_file, dunder_line, msg, dunder_func);
    abort();
}
noreturn void _LmcAssert_FailNoMsg(const char* dunder_file, int dunder_line, const char* dunder_func) {
    fprintf(stderr, "%s:%i LmcAssert_ASSERT() failed in %s, aborting", dunder_file, dunder_line, dunder_func);
    abort();
}

void _LmcAssert_AssertMsgFatal_Func(bool cond, const char* msg, const char* dunder_file, int dunder_line, const char* dunder_func) {
    if(!cond) _LmcAssert_FailWithMsg(msg, dunder_file, dunder_line, dunder_func);
}

void _LmcAssert_AssertFatal_Func(bool cond, const char* dunder_file, int dunder_line, const char* dunder_func) {
    if(!cond) _LmcAssert_FailNoMsg(dunder_file, dunder_line, dunder_func);
}

#endif
