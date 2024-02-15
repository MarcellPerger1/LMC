#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <stdbool.h>

#include "lmc_runtime_lib/concise_inttypes.h"
#include "lmc_runtime_lib/lmc_assert.h"
#include "lmc_runtime_lib/lmc_mem.h"



int main(int argc, char** argv) {
    (void)argc;(void)argv;
    wprintf(L"Hello world, %zi\n", sizeof(LmcMemT));
    return 0;
}
