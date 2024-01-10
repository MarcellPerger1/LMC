"""An interpreter for running base 10 LMC assembly.

Features:

- Implements all LMC instructions
- Also implements the non-standard OTC instruction from Peter Higginson's
  LMC simulator at https://peterhigginson.co.uk/lmc.
  This can be disabled by passing extensions=False to ``InterpreterB10``
- Options to have values/memory wrap around
- 3 ways to run this:

  - Run list[int] memory directly using the ``InterpreterB10(...)``,
  - Run text source code using ``InterpreterB10.from_source(...)``,
    see ``AsmParser``
  - Run list[Data | Instruction] using ``Interpreter.from_instr_list()``,
    this is mainly for programmatic use"""
from __future__ import annotations

from LMC_interp.base_instruction import Instruction
from LMC_interp.data_instruction import Data
from LMC_interp.errors import (
    ProgramOOBError, ProgramIpOOB, ProgramReadOOB, ProgramWriteOOB,
    ProgramJmpOOB, ExtensionDisabledError)
from LMC_interp.instruction_conv import instructions_to_memory
from LMC_interp.instructions import ensure_instr_registered
from LMC_interp.io_mgr import IOMgr
from LMC_interp.parse_asm import AsmParser


class InterpreterB10:
    # Here, memory_size can't be easily changed but value_range can.
    memory_size: int = 100  # ClassVar, immut but readable from inst
    value_range: tuple[int, int] = (-999, 999)  # ClassVar, immut from inst

    # region init
    def __init__(self, initial_memory: list[int] | None = None,
                 wrap_memory=False, wrap_values=True, extensions=True):
        self.wrap_memory = wrap_memory
        self.wrap_values = wrap_values
        self.extensions = extensions
        self.memory = self._make_memory_obj(initial_memory)
        self.io = IOMgr(self)
        self.ip = 0
        """Instruction pointer (PC)"""
        self.cir: int | None = None
        """Current instruction register (CIR) - Probably internal"""
        self.acc_internal = 0
        """Accumulator (ACC) - Internal, prefer to use .acc which wraps on write"""
        self.is_halted = False
        self.decoded_instr: Instruction | None = None

    def _make_memory_obj(self, initial_memory: list[int] | None) -> list[int]:
        if initial_memory is None:
            return [0] * self.memory_size
        if len(initial_memory) > self.memory_size:
            raise ValueError("initial_memory doesn't fit in the memory size")
        # fill rest (if any) with zeroes
        extra_padding = self.memory_size - len(initial_memory)
        return initial_memory + [0] * extra_padding

    @classmethod
    def from_instr_list(cls, instructions: list[int | Instruction | Data],
                        wrap_memory=False, wrap_values=True, extensions=True):
        return cls(instructions_to_memory(instructions),
                   wrap_memory, wrap_values, extensions)

    @classmethod
    def from_source(cls, source: str, wrap_memory=False, wrap_values=True,
                    extensions=True, append_hlt=False):
        p = AsmParser(source, extensions, append_hlt).parse()
        return cls(p.memory, wrap_memory, wrap_values, extensions)

    # endregion

    # I wish I could do separate `impl` blocks like in Rust to
    # separate this logic out but PyCharm regions will have to do
    # region FDE cycle
    def fetch(self):
        self.normalize_ip()
        self.cir = self.memory[self.ip]
        self.ip += 1

    def decode(self):
        self.decoded_instr: Instruction = Instruction.get_instr(self.cir)

    def execute(self):
        self.decoded_instr.run(self)

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


ensure_instr_registered()
