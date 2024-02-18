from __future__ import annotations

from typing import Self

from LMC_interp.base_instruction import Instruction
from LMC_interp.data_instruction import Data
from LMC_interp.errors import (
    ProgramReadOOB, ProgramWriteOOB, ProgramJmpOOB,
    ExtensionDisabledError, ProgramOOBError, ProgramIpOOB, InvalidOpcodeError,
    InvalidOperandError,
)
from LMC_interp.parse_asm import AsmParser

MEM_SIZE_DEFAULT = 0x10000  # 2**16


class InterpB2:
    value_range = (-(1 << 31), (1 << 31) - 1)

    def __init__(self, memory: list[int] | None = None,
                 mem_size: int = MEM_SIZE_DEFAULT, extensions: bool = True,
                 wrap_memory=False, inp_prompt: str = '>? '):
        self.memory_size = mem_size
        self.memory = self._make_memory_obj(memory)
        self.extensions = extensions
        self.wrap_memory = wrap_memory
        self.inp_prompt = inp_prompt
        self.io = IOMgrB2(self)
        self.wrap_values = True
        self.cir = None
        self.decoded_instr = None
        self.ip = 0
        self.acc_internal = 0
        self.n_instr = 0
        self.is_halted = False

    # region init
    @classmethod
    def from_instr_list(cls, instructions: list[int | Instruction | Data],
                        mem_size: int = MEM_SIZE_DEFAULT,
                        extensions: bool = True, wrap_memory=False,
                        inp_prompt: str = '>? '):
        return cls(cls._instr_b10_list_to_b2(instructions), mem_size,
                   extensions, wrap_memory, inp_prompt)

    @classmethod
    def from_source(cls: type[Self], source: str, mem_size: int = MEM_SIZE_DEFAULT,
                    extensions: bool = True, wrap_memory=False,
                    append_hlt: bool = False, inp_prompt: str = '>? ') -> Self:
        p = AsmParser(source, extensions, append_hlt).parse()
        # NOTE: can't use .memory as that's base10
        return cls.from_instr_list(p.instructions, mem_size, extensions,
                                   wrap_memory, inp_prompt)

    def _make_memory_obj(self, initial_memory: list[int] | None) -> list[int]:
        if initial_memory is None:
            return [0] * self.memory_size
        if len(initial_memory) > self.memory_size:
            raise ValueError("initial_memory doesn't fit in the memory size")
        # fill rest (if any) with zeroes
        extra_padding = self.memory_size - len(initial_memory)
        return initial_memory + [0] * extra_padding
    # endregion

    # region convert (@classmethod)
    @classmethod
    def _instr_b10_list_to_b2(
            cls, instr_list: list[Instruction | Data | int]) -> list[int]:
        return [cls._instr_1_b10_to_int_b2(instr) for instr in instr_list]

    @classmethod
    def _b2_from_opcode_operand(cls, opcode: int, operand: int) -> int:
        assert 0 <= operand < 100
        result = (1 << 27) * opcode + operand
        assert cls.value_range[0] <= result <= cls.value_range[1]
        return result

    @classmethod
    def _instr_1_b10_to_int_b2(cls, instr: Instruction | Data | int) -> int:
        if isinstance(instr, int):
            return instr
        if isinstance(instr, Data):
            return instr.data
        assert isinstance(instr, Instruction)
        operand = instr.get_b10_operands()
        opcode = instr.get_b10_opcode()
        return cls._b2_from_opcode_operand(opcode, operand)
    # endregion

    # region FDE cycle
    def fetch(self):
        self.normalize_ip()
        self.cir = self.memory[self.ip]
        self.ip += 1
        self.n_instr += 1

    def decode(self):
        self.decoded_instr = (self.cir >> 27, self.cir & 0x07_FF_FF_FF)

    def execute(self):
        opcode, operand = self.decoded_instr
        match opcode:
            case 0:  # HLT
                self.is_halted = True
            case 1:  # ADD
                self.acc += self.get(operand)
            case 2:  # SUB
                self.acc -= self.get(operand)
            case 3:  # STA
                self.set(operand, self.acc)
            case 4:
                raise InvalidOpcodeError("Opcode 4 is invalid (unused)")
            case 5:  # LDA
                self.acc = self.get(operand)
            case 6:  # BRA
                self.jmp(operand)
            case 7:  # BRZ
                if self.acc == 0:
                    self.jmp(operand)
            case 8:  # BRP
                if self.acc >= 0:
                    self.jmp(operand)
            case 9:  # IO
                match operand:
                    case  1:  # INP
                        self.acc = self.io.read_num()
                    case  2:  # OUT
                        self.io.write_num(self.acc)
                    case 22:  # OTC
                        self.ext_otc__expect_enabled()
                        self.io.write_char(self.acc)
                    case _:
                        raise InvalidOperandError(f"Bad IO operand: {operand}")
            case _:
                raise InvalidOpcodeError(f"Invalid opcode: {opcode}")

    def run(self):
        while not self.is_halted:
            self.fetch()
            self.decode()
            self.execute()
    # endregion

    # region  utils used by *Instr
    def get(self, addr: int) -> int:
        err = ProgramReadOOB("Attempt to read outside of memory", hint_wrap_memory=True)
        return self.memory[self.normalize_addr(addr, err)]

    def set(self, addr: int, value: int):
        err = ProgramWriteOOB("Attempt to write outside of memory", hint_wrap_memory=True)
        self.memory[self.normalize_addr(addr, err)] = self.normalize_value(value)

    @property
    def acc(self) -> int:
        return self.acc_internal

    @acc.setter
    def acc(self, value: int):
        self.acc_internal = self.normalize_value(value)

    def jmp(self, addr: int):
        err = ProgramJmpOOB("Program branched outside of memory", hint_wrap_memory=True)
        self.ip = self.normalize_addr(addr, err)

    # endregion

    # region extensions: ext_otc__*
    def ext_otc__enabled(self):
        return self.extensions

    def ext_otc__expect_enabled(self):
        if not self.ext_otc__enabled():
            raise ExtensionDisabledError(
                "The non-standard OTC instruction (code 922) is not enabled"
                " (HINT: pass extensions=True to enable it)")

    # endregion

    # region bound checking/wrapping etc.
    def is_addr_in_bounds(self, addr: int) -> bool:
        return 0 <= addr < len(self.memory)

    def normalize_addr(self, addr: int, err: Exception = None) -> int:
        if self.is_addr_in_bounds(addr):
            return addr
        if self.wrap_memory:
            return addr % len(self.memory)
        raise err if err is not None else ProgramOOBError(
            "Attempt to access out-of-bounds memory")

    def normalize_value(self, value: int) -> int:  # noexcept
        if self.wrap_values:
            # convert desired -999..=999 -> 0..=(999+999)
            value -= self.value_range[0]
            # end_incl = 999+999 = 999 - (-999)
            maxvalue_incl = self.value_range[1] - self.value_range[0]
            maxvalue_excl = maxvalue_incl + 1
            value %= maxvalue_excl
            # convert back to orig range
            value += self.value_range[0]
        return value

    def normalize_ip(self):
        err = ProgramIpOOB("Instruction pointer went outside of memory",
                           hint_wrap_memory=True)
        self.ip = self.normalize_addr(self.ip, err)
    # endregion


class IOMgrB2:
    def __init__(self, interp: InterpB2):
        self.interp = interp  # just for the config (e.g. value_range)
        self.is_line_mode = False

    def write_num(self, num: int):
        print(num, end='' if self.is_line_mode else '\n')

    def write_char(self, ascii_value: int):
        # This function starts a 'line' if not already started and
        #  everything will be output onto that single line without any spaces
        #  until \n is output to end the line
        #  (e.g. OTC 'a'; OUT 1; OUT 2; prints 'a12' NOT 'a\n 1\n 2\n').
        # After the line is finished, outputting numbers goes back
        #  to the usual behavior of 1 number / line; outputting a char will
        #  put it back into the 'line' mode.
        # This is so that code not using OTC gets the expected behavior
        #  while allowing easier mixing of text and numbers on a single line
        #  and (as long as all 'line'-s are terminated), using OTC in one part
        #  of the program doesn't impact printing done by another part
        #  of the program
        # So this way it's both backwards-compatible and easier to mix the two
        char = chr(ascii_value)
        print(char, end='')
        if char == '\n':
            self.is_line_mode = False
        else:
            self.is_line_mode = True

    def read_num(self) -> int:
        num_range = self.interp.value_range
        while True:
            try:
                value = int(input(self.interp.inp_prompt))
            except ValueError:
                print('Input must be an integer')
                continue
            if not self.interp.wrap_values:
                return value  # allow any value if no wrap_values
            if num_range[0] <= value <= num_range[1]:
                return value
            else:
                print('Input out of range')
