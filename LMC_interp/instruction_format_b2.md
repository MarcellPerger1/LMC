# Instruction format for binary instructions:
Signed 32-bit integers: `<opcode: 5 bits> <operand: 27 bits>`

## Opcodes

| opcode        | instruction           | operand                                   |
|---------------|-----------------------|-------------------------------------------|
| `00000` (`0`) | `HLT`                 | ignored                                   |
| `00001` (`1`) | `ADD`                 | addr of arg 2                             |
| `00010` (`2`) | `SUB`                 | addr of arg 2                             |
| `00011` (`3`) | `STA` / `STO`         | addr to store at                          |
| `00100` (`4`) | *(unused opcode)*     |                                           |
| `00101` (`5`) | `LDA`                 | addr to load from                         |
| `00110` (`6`) | `BRA`                 | addr to jump to                           |
| `00111` (`7`) | `BRZ`                 | addr to jump to                           |
| `01000` (`8`) | `BRP`                 | addr to jump to                           |
| `01001` (`9`) | `INP` / `OUT` / `OTC` | [see below](#operand-for-io-instructions) |

### Operand for I/O instructions

| Instruction | Operand         |
|-------------|-----------------|
| `INP`       | `...00001` (1)  |
| `OUT`       | `...00010` (2)  |
| `OTC`       | `...10110` (22) |
