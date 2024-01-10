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

if __name__ == '__main__':
    from LMC_interp.interpreter_b10 import InterpreterB10
    # InterpreterB10.from_source(PRG).run()
    InterpreterB10.from_source(PRG2, wrap_values=False).run()
