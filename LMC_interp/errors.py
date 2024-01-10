from __future__ import annotations

WRAP_MEMORY_HINT = (
    ' (HINT: init InterpreterB10 with wrap_memory=True to enable memory wrapping)')


class LMCError(Exception):
    pass


class ProgramOOBError(LMCError):
    def __init__(self, msg: str = '', hint_wrap_memory=False):
        if msg and hint_wrap_memory:
            msg += WRAP_MEMORY_HINT
        super().__init__(msg)


class ProgramIpOOB(ProgramOOBError):
    pass


class ProgramReadOOB(ProgramOOBError):
    pass


class ProgramWriteOOB(ProgramOOBError):
    pass


class ProgramJmpOOB(ProgramOOBError):
    pass  # this probably should never be raised as all addr to jmp to are from the operand


class InvalidInstructionError(LMCError):
    pass


class InvalidOpcodeError(InvalidInstructionError):
    pass


class InvalidOperandError(InvalidInstructionError):
    pass


class ExtensionDisabledError(InvalidInstructionError):
    pass
