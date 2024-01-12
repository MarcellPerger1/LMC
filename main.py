from LMC_interp.interpreter_b10 import InterpreterB10
from LMC_interp.parse_asm import AsmParser

PRG = '''\
    INP   // this is a comment
// another comment
    ADD one
    OUT
    HLT
one DAT 1
'''

PRG2 = '''
// Outputs the minimum of the 2 numbers, provided there's no overflow
        INP
        STA x
        INP
        SUB x
        BRP addx
        LDA zero
addx    ADD x
        OUT 
zero    HLT
x       DAT
'''


def readfile(path: str):
    with open(path) as f:
        return f.read()


if __name__ == '__main__':
    # InterpreterB10.from_source(PRG).run()
    # InterpreterB10.from_source(PRG2, wrap_values=False).run()
    import time
    t0 = time.perf_counter()
    src = readfile("sort_5_nums.lmc")
    t1 = time.perf_counter()
    ip = InterpreterB10.from_source(src)
    t2 = time.perf_counter()
    ip.run()
    t3 = time.perf_counter()
    print(f'Read file:  {(t1 - t0)*1000:>8.3f}ms')
    print(f'Parse code: {(t2 - t1)*1000:>8.3f}ms')
    print(f'Run code:   {(t3 - t2)*1000:>8.3f}ms')
    print(f'Total time: {(t3 - t0)*1000:>8.3f}ms')
    parsed = AsmParser(src).parse()
    print(f'Instructions in file: {len(parsed.instructions):>5}')
    print(f'Instructions ran:     {ip.n_instr:>5}')
