## Instruction format for base 10 instructions:  
`<opcode: 0-9> <operand: 00-99>`

## Opcode list:

| opcode | instruction           | operand                         |
|--------|-----------------------|---------------------------------|
| `0xx`  | `HLT`                 | ignored                         |
| `1xx`  | `ADD`                 | addr of arg 2                   |
| `2xx`  | `SUB`                 | addr of arg 2                   |
| `3xx`  | `STA` / `STO`         | addr to store at                |
| `4xx`  | *(unused opcode)*     |                                 |
| `5xx`  | `LDA`                 | addr to load from               |
| `6xx`  | `BRA`                 | addr to jump to                 |
| `7xx`  | `BRZ`                 | addr to jump to                 |
| `8xx`  | `BRP`                 | addr to jump to                 |
| `9xx`  | `INP` / `OUT` / `OTC` | `INP`: 1, `OUT`: 2, `OTC`: 22\* |

*`OTC` is a non-standard instruction