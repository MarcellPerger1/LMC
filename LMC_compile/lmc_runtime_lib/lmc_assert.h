#ifndef _LMC_ASSERT_H
#define _LMC_ASSERT_H

#include <stdio.h>
#include <stdlib.h>
#include <stdbool.h>
#include <stdnoreturn.h>

// LmcAssert_FATAL / LmcAssert_ASSERT

#define _LmcAssert_INTERN_GETARG3(a1,a2,a3,...) a3
// Error messages gonna be real bad this one
#define LmcAssert_FATALX(...) _LmcAssert_INTERN_GETARG3(__VA_ARGS__, _LmcAssert_AssertMsgFatal_Func, _LmcAssert_AssertFatal_Func)\
    (__VA_ARGS__, __FILE__, __LINE__, __func__)
#define LmcAssert_FATAL1(cond) _LmcAssert_AssertFatal_Func(cond, __FILE__, __LINE__, __func__)
#define LmcAssert_FATAL2(cond, msg) _LmcAssert_AssertMsgFatal_Func(cond, msg, __FILE__, __LINE__, __func__)


noreturn void _LmcAssert_FailWithMsg(const char* msg, const char* dunder_file, int dunder_line, const char* dunder_func) {
    fwprintf(stderr, L"%hs:%i %hs (in function %hs)", dunder_file, dunder_line, msg, dunder_func);
    abort();
}
noreturn void _LmcAssert_FailNoMsg(const char* dunder_file, int dunder_line, const char* dunder_func) {
    fwprintf(stderr, L"%hs:%i LmcAssert_ASSERT() failed in %hs, aborting", dunder_file, dunder_line, dunder_func);
    abort();
}

void _LmcAssert_AssertMsgFatal_Func(bool cond, const char* msg, const char* dunder_file, int dunder_line, const char* dunder_func) {
    if(!cond) _LmcAssert_FailWithMsg(msg, dunder_file, dunder_line, dunder_func);
}

void _LmcAssert_AssertFatal_Func(bool cond, const char* dunder_file, int dunder_line, const char* dunder_func) {
    if(!cond) _LmcAssert_FailNoMsg(dunder_file, dunder_line, dunder_func);
}

// LmcAssert_UNREACHABLE
#define _LmcAssert_UNREACHABLE2_ignore0(_ignore0, file, line, func) _LmcAssert_UnreachableFatal(file, line, func)
#define _LmcAssert_UNREACHABLE3_ignore0(_ignore0, msg, file, line, func) _LmcAssert_UnreachableMsgFatal(msg, file, line, func)
#define _LmcAssert_UNREACHABLE_ignore0(...) _LmcAssert_INTERN_GETARG3(__VA_ARGS__, \
 _LmcAssert_UNREACHABLE3_ignore0(__VA_ARGS__, __FILE__, __LINE__, __func__),\
 _LmcAssert_UNREACHABLE2_ignore0(__VA_ARGS__, __FILE__, __LINE__, __func__))
// Again, really bad error messages with this one, expecially as it uses the non-standard
//  (but widely implemented) `##__VA_ARGS__` (also IDE may/will complain)
#define LmcAssert_UNREACHABLEX(...) _LmcAssert_UNREACHABLE_ignore0(false, ##__VA_ARGS__)
#define LmcAssert_UNREACHABLE0() _LmcAssert_UnreachableFatal(__FILE__, __LINE__, __func__)
#define LmcAssert_UNREACHABLE1(msg) _LmcAssert_UnreachableMsgFatal(msg, __FILE__, __LINE__, __func__)

noreturn void _LmcAssert_UnreachableFatal(const char* dunder_file, int dunder_line, const char* dunder_func) {
    fwprintf(stderr, L"%hs:%i LmcAssert_UNREACHABLE() reached, aborting (in function %hs)", dunder_file, dunder_line, dunder_func);
    abort();
}
noreturn void _LmcAssert_UnreachableMsgFatal(const char* msg, const char* dunder_file, int dunder_line, const char* dunder_func) {
    fwprintf(stderr, L"%hs:%i %hs, aborting (in function %hs)", dunder_file, dunder_line, msg, dunder_func);
    abort();
}

#endif
