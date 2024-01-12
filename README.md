Things to do with the [Little Man Computer (LMC)](https://en.wikipedia.org/wiki/Little_man_computer).
## [LMC_interp](https://github.com/MarcellPerger1/LMC/tree/main/LMC_interp)
- An LMC interpreter written in Python, compatible with [Peter Higginson's LMC simulator](https://peterhigginson.co.uk/lmc).
- Options to have memory addresses/values wrap around / not wrap around.
- Also implements the non-standard `OTC` instruction (code 922) to output characters.
- Fast: `0.2ms` to parse 78 lines, `0.3ms` to run 173 instructions (not counting I/O).
- Can disable non-standard features with `extensions=False`.
